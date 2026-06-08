# -*- coding: utf-8 -*-
import os

import resend

resend.api_key = os.getenv("RESEND_API_KEY", "")

_FRONTEND_URL = "https://reqflow-requirements.vercel.app"


class NotificationService:

    @staticmethod
    def enviar_cambio_estado(
        email_destinatario: str,
        titulo_requerimiento: str,
        estado_nuevo: str,
        nombre_proyecto: str = "ReqFlow",
        requerimiento_id: int = None,
    ) -> None:
        if not resend.api_key:
            print("RESEND_API_KEY no configurada - email omitido")
            return

        link = ""
        if requerimiento_id:
            link = f"{_FRONTEND_URL}/requerimientos/{requerimiento_id}"

        boton = (
            f"<a href='{link}' style='display:inline-block;background:#0f2557;"
            f"color:white;padding:12px 24px;border-radius:6px;text-decoration:none;"
            f"margin-top:8px;'>Ver requerimiento</a>"
            if link else ""
        )

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
            <div style="background:#0f2557;padding:20px;border-radius:8px 8px 0 0;">
                <h1 style="color:white;margin:0;">ReqFlow</h1>
                <p style="color:#a0b4d6;margin:5px 0 0;">Proyecto: {nombre_proyecto}</p>
            </div>
            <div style="padding:24px;border:1px solid #e2e8f0;border-radius:0 0 8px 8px;">
                <h2 style="color:#1a202c;">Cambio de estado en tu requerimiento</h2>
                <p style="color:#4a5568;">
                    El requerimiento <strong>{titulo_requerimiento}</strong>
                    ha cambiado de estado a:
                </p>
                <div style="background:#ebf8ff;border-left:4px solid #3182ce;
                            padding:12px 16px;margin:16px 0;border-radius:4px;">
                    <strong style="color:#2b6cb0;font-size:18px;">{estado_nuevo}</strong>
                </div>
                {boton}
                <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;">
                <p style="color:#718096;font-size:14px;">
                    Este email fue enviado por ReqFlow.
                    Si no esperabas este mensaje puedes ignorarlo.
                </p>
            </div>
        </div>
        """

        try:
            resend.Emails.send({
                "from": "ReqFlow <onboarding@resend.dev>",
                "to": email_destinatario,
                "subject": f"[{nombre_proyecto}] Requerimiento actualizado: {estado_nuevo}",
                "html": html,
            })
        except Exception as e:
            print(f"Error enviando email Resend: {e}")
