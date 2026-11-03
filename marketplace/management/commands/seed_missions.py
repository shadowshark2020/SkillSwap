from django.core.management.base import BaseCommand
from marketplace.models import MissionTemplate, UserMission

class Command(BaseCommand):
    help = 'Actualiza las misiones con descripciones detalladas de cómo completarlas.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Actualizando plantillas de misiones...")
        UserMission.objects.all().delete()
        MissionTemplate.objects.all().delete()

        missions_data = []

        # ==========================================
        # 1. MISIONES DIARIAS
        # ==========================================
        dailies = [
            (
                "Explorador del Marketplace", 
                "¿Cómo completarla?\n1. Dirígete a la sección 'Explorar' en el menú principal.\n2. Navega por las diferentes categorías de clases.\n3. Visualiza las habilidades disponibles hoy en la plataforma.", 
                "alumno", 1, 10, "explore_catalog"
            ),
            (
                "Primer Contacto en Chat", 
                "¿Cómo completarla?\n1. Entra a 'Mis Mensajes' (Inbox).\n2. Selecciona una sala de chat activa con un compañero o profesor.\n3. Envía al menos un mensaje de texto para fomentar la colaboración.", 
                "ambos", 1, 10, "send_message"
            ),
            (
                "Revisión de Panel", 
                "¿Cómo completarla?\n1. Haz clic en tu perfil o ve a 'Mi Panel'.\n2. Revisa el estado general de tus solicitudes de clases y notificaciones recientes.", 
                "ambos", 1, 10, "check_dashboard"
            ),
            (
                "Lectura de Habilidad", 
                "¿Cómo completarla?\n1. Entra al catálogo de clases en 'Explorar'.\n2. Haz clic sobre cualquier clase que te llame la atención para ver sus detalles completos y leer su descripción.", 
                "alumno", 1, 10, "view_skill"
            ),
            (
                "Estado de Maestro", 
                "¿Cómo completarla?\n1. Ve a tu sección 'Mis Clases'.\n2. Comprueba que tus publicaciones estén activas, con precios correctos y listas para recibir alumnos.", 
                "maestro", 1, 10, "active_check"
            ),
        ]
        for title, desc, role, count, reward, key in dailies:
            missions_data.append({"title": title, "description": desc, "mission_type": "daily", "target_role": role, "target_count": count, "reward_amount": reward, "action_key": key})

        # ==========================================
        # 2. MISIONES SEMANALES
        # ==========================================
        weeklies = [
            (
                "Estudiante Constante", 
                "¿Cómo completarla?\n1. Explora el catálogo de clases.\n2. Solicita al menos 3 clases diferentes con distintos profesores a lo largo de la semana.", 
                "alumno", 3, 25, "request_class"
            ),
            (
                "Maestro Dedicado", 
                "¿Cómo completarla?\n1. Revisa las solicitudes de clases pendientes de tus alumnos.\n2. Acepta y coordina al menos 2 solicitudes de clases en el transcurso de la semana.", 
                "maestro", 2, 25, "accept_class"
            ),
            (
                "Comunicación Fluida", 
                "¿Cómo completarla?\n1. Interactúa regularmente en las salas de chat de tus clases.\n2. Envía un acumulado de 15 mensajes colaborativos durante la semana.", 
                "ambos", 15, 25, "chat_activity"
            ),
            (
                "Clase Concluida con Éxito", 
                "¿Cómo completarla?\n1. Lleva a cabo una sesión de aprendizaje o enseñanza acordada.\n2. Haz clic en el botón de finalizar/completar clase en el sistema junto a la contraparte.", 
                "ambos", 1, 30, "complete_class"
            ),
            (
                "Crítico Constructivo", 
                "¿Cómo completarla?\n1. Al finalizar una clase como alumno, ve al apartado correspondiente.\n2. Deja una reseña detallada y calificación con estrellas.", 
                "alumno", 2, 20, "add_review"
            ),
            (
                "Búsqueda Profunda", 
                "¿Cómo completarla?\n1. Utiliza los filtros avanzados por categoría en el explorador de clases al menos 5 veces durante la semana.", 
                "alumno", 5, 20, "filter_search"
            ),
            (
                "Renovación de Saberes", 
                "¿Cómo completarla?\n1. Visita y revisa los perfiles públicos detallados de al menos 3 profesores diferentes en el marketplace.", 
                "alumno", 3, 20, "view_teachers"
            ),
            (
                "Red de Apoyo", 
                "¿Cómo completarla?\n1. Abre regularmente tu menú de notificaciones.\n2. Mantén al día tus interacciones y avisos semanales de la comunidad.", 
                "ambos", 5, 15, "check_notifications"
            ),
            (
                "Gestión de Horarios", 
                "¿Cómo completarla?\n1. Ingresa periódicamente a tu panel de 'Mis Clases'.\n2. Revisa, edita o actualiza el estado de tus ofertas educativas semanales.", 
                "maestro", 3, 20, "manage_skills"
            ),
            (
                "Maratón Semanal de Actividad", 
                "¿Cómo completarla?\n1. Ingresa a la plataforma y realiza actividades en al menos 3 días distintos de la semana para mantener tu constancia.", 
                "ambos", 3, 35, "weekly_streak"
            ),
        ]
        for title, desc, role, count, reward, key in weeklies:
            missions_data.append({"title": title, "description": desc, "mission_type": "weekly", "target_role": role, "target_count": count, "reward_amount": reward, "action_key": key})

        # ==========================================
        # 3. MISIONES PERMANENTES (Ordenadas del 1 al 100)
        # ==========================================
        perm_titles = [
            "Pionero de SkillSwap", "Primeros Pasos en el Aprendizaje", "Conector de Saberes", "Maestro Novato",
            "Estudiante Entusiasta", "Conversador Habitual", "Explorador de Categorías", "Primer Intercambio Exitoso",
            "Crítico Académico", "Promotor del Conocimiento", "Mentor en Crecimiento", "Aprendiz Dedicado",
            "Intercambio Global", "Gestor de Clases", "Perfil Verificado", "Coleccionista de SkillCoins",
            "Embajador de la Comunidad", "Experto en Redes", "Formador de Talentos", "Sabiduría Compartida",
            "Cátedra Abierta", "Ruta de Estudio", "Constancia de Acero", "Libro Abierto", "Maestría en Línea"
        ]

        for i in range(1, 101):
            if i <= len(perm_titles):
                title = perm_titles[i - 1]
            else:
                title = f"Maestría Global en Redes #{i}"

            desc = (
                f"¿Cómo completarla?\n"
                f"1. Acumula participación global y constancia continua en SkillSwap.\n"
                f"2. Alcanza el objetivo acumulativo requerido de {i * 5} acciones o metas cumplidas en la plataforma para desbloquear este logro histórico nivel {i}."
            )

            missions_data.append({
                "title": title,
                "description": desc,
                "mission_type": "permanent",
                "target_role": "ambos",
                "target_count": i * 5,
                "reward_amount": 100 + (i * 10),
                "action_key": f"permanent_milestone_{i}"
            })

        for data in missions_data:
            MissionTemplate.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(f"¡Se han creado {len(missions_data)} misiones con guías detalladas de cómo completarlas!"))