from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_application_approved_email(self, user_email: str):
    try:
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table width="500" cellpadding="0" cellspacing="0"
                            style="background:#ffffff; border-radius:8px;
                                   box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                            <tr>
                                <td align="center"
                                    style="background:#16A34A; padding:32px;
                                           border-radius:8px 8px 0 0;">
                                    <h1 style="color:#ffffff; margin:0; font-size:24px;">
                                        🎉 Permohonan Disetujui!
                                    </h1>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 32px 40px;">
                                    <p style="color:#374151; font-size:16px; margin:0 0 16px;">
                                        Halo 👋
                                    </p>
                                    <p style="color:#374151; font-size:15px; line-height:1.6; margin:0 0 24px;">
                                        Selamat! Permohonan kamu untuk menjadi seller telah
                                        <strong>disetujui</strong>. Kamu sekarang bisa membuat
                                        toko dan mulai berjualan.
                                    </p>
                                    <p style="color:#9CA3AF; font-size:12px; margin:16px 0 0;">
                                        ⚠️ Segera lengkapi profil toko kamu untuk mulai berjualan.
                                    </p>
                                </td>
                            </tr>

                            <tr>
                                <td align="center"
                                    style="padding:20px; border-top:1px solid #E5E7EB;">
                                    <p style="color:#9CA3AF; font-size:12px; margin:0;">
                                        © 2026 Commerce App · Dikirim otomatis, jangan dibalas.
                                    </p>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        send_mail(
            subject="🎉 Permohonan Seller Disetujui — Commerce App",
            message="Selamat! Permohonan kamu untuk menjadi seller telah disetujui.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )

    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_application_rejected_email(self, user_email: str, reject_note: str):
    try:
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0; padding:0; background-color:#f4f4f4; font-family: Arial, sans-serif;">
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td align="center" style="padding: 40px 0;">
                        <table width="500" cellpadding="0" cellspacing="0"
                            style="background:#ffffff; border-radius:8px;
                                   box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

                            <tr>
                                <td align="center"
                                    style="background:#DC2626; padding:32px;
                                           border-radius:8px 8px 0 0;">
                                    <h1 style="color:#ffffff; margin:0; font-size:24px;">
                                        Permohonan Ditolak
                                    </h1>
                                </td>
                            </tr>

                            <tr>
                                <td style="padding: 32px 40px;">
                                    <p style="color:#374151; font-size:16px; margin:0 0 16px;">
                                        Halo 👋
                                    </p>
                                    <p style="color:#374151; font-size:15px; line-height:1.6; margin:0 0 16px;">
                                        Maaf, permohonan kamu untuk menjadi seller
                                        <strong>ditolak</strong> dengan alasan:
                                    </p>
                                    <p style="background:#FEF2F2; padding:12px;
                                              border-radius:4px; color:#DC2626;
                                              font-size:14px; margin:0 0 16px;">
                                        {reject_note}
                                    </p>
                                    <p style="color:#374151; font-size:14px; line-height:1.6;">
                                        Kamu bisa mengajukan permohonan kembali setelah
                                        memperbaiki kekurangan tersebut.
                                    </p>
                                    <p style="color:#9CA3AF; font-size:12px; margin:16px 0 0;">
                                        ⚠️ Jika kamu merasa ini adalah kesalahan, silakan
                                        hubungi tim support kami.
                                    </p>
                                </td>
                            </tr>

                            <tr>
                                <td align="center"
                                    style="padding:20px; border-top:1px solid #E5E7EB;">
                                    <p style="color:#9CA3AF; font-size:12px; margin:0;">
                                        © 2026 Commerce App · Dikirim otomatis, jangan dibalas.
                                    </p>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        send_mail(
            subject="Permohonan Seller Ditolak — Commerce App",
            message=f"Permohonan kamu ditolak. Alasan: {reject_note}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )

    except Exception as exc:
        raise self.retry(exc=exc)