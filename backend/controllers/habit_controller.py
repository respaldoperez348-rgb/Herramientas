from flask import Blueprint, request, jsonify

from backend.services.habit_service import HabitService


habit_controller = Blueprint(
    "habit_controller",
    __name__
)

habit_service = HabitService()


@habit_controller.route(
    "/habitos",
    methods=["GET"]
)
def obtener_habitos():
    habitos = habit_service.obtener_habitos()

    return jsonify([
        habit.to_dict()
        for habit in habitos
    ]), 200


@habit_controller.route(
    "/habitos/<int:habit_id>",
    methods=["GET"]
)
def obtener_habito(habit_id):
    habit = habit_service.obtener_habito(habit_id)

    if habit is None:
        return jsonify({"error": "Hábito no encontrado."}), 404

    return jsonify(habit.to_dict()), 200


@habit_controller.route(
    "/habitos",
    methods=["POST"]
)
def crear_habito():
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "Debe enviar los datos del hábito."}), 400

    try:
        habit = habit_service.crear_habito(
            nombre=datos.get("nombre", ""),
            descripcion=datos.get("descripcion", ""),
            frecuencia=datos.get("frecuencia", "diaria"),
            hora_recordatorio=datos.get("hora_recordatorio")
        )

        return jsonify({
            "mensaje": "Hábito creado correctamente.",
            "habit": habit.to_dict()
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@habit_controller.route(
    "/habitos/<int:habit_id>",
    methods=["PUT"]
)
def actualizar_habito(habit_id):
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "Debe enviar los datos a actualizar."}), 400

    try:
        habit = habit_service.actualizar_habito(habit_id, datos)

        if habit is None:
            return jsonify({"error": "Hábito no encontrado."}), 404

        return jsonify({
            "mensaje": "Hábito actualizado correctamente.",
            "habit": habit.to_dict()
        }), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400


@habit_controller.route(
    "/habitos/<int:habit_id>",
    methods=["DELETE"]
)
def eliminar_habito(habit_id):
    eliminado = habit_service.eliminar_habito(habit_id)

    if not eliminado:
        return jsonify({"error": "Hábito no encontrado."}), 404

    return jsonify({"mensaje": "Hábito eliminado correctamente."}), 200


@habit_controller.route(
    "/habitos/<int:habit_id>/completar",
    methods=["PATCH"]
)
def completar_habito(habit_id):
    habit = habit_service.completar_habito(habit_id)

    if habit is None:
        return jsonify({"error": "Hábito no encontrado."}), 404

    return jsonify({
        "mensaje": "Hábito marcado como completado.",
        "habit": habit.to_dict()
    }), 200
