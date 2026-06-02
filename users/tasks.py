from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .tokens import generate_verification_token

# tasks.py

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, user_email: str):
    try:
        token      = generate_verification_token(user_email)
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

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

                            <!-- HEADER -->
                            <tr>
                                <td align="center"
                                    style="background:#4F46E5; padding:32px;
                                           border-radius:8px 8px 0 0;">
                                    <h1 style="color:#ffffff; margin:0; font-size:24px;">
                                        Verifikasi Email Anda
                                    </h1>
                                </td>
                            </tr>

                            <!-- BODY -->
                            <tr>
                                <td style="padding: 32px 40px;">
                                    <p style="color:#374151; font-size:16px; margin:0 0 16px;">
                                        Halo 👋
                                    </p>
                                    <p style="color:#374151; font-size:15px; line-height:1.6; margin:0 0 24px;">
                                        Terima kasih telah mendaftar! Klik tombol di bawah
                                        untuk mengaktifkan akun kamu.
                                    </p>

                                    <!-- BUTTON -->
                                    <table width="100%" cellpadding="0" cellspacing="0">
                                        <tr>
                                            <td align="center" style="padding: 8px 0 24px;">
                                                <a href="{verify_url}"
                                                   style="background:#4F46E5; color:#ffffff;
                                                          text-decoration:none; padding:14px 32px;
                                                          border-radius:6px; font-size:15px;
                                                          font-weight:bold; display:inline-block;">
                                                    ✅ Verifikasi Sekarang
                                                </a>
                                            </td>
                                        </tr>
                                    </table>

                                    <p style="color:#6B7280; font-size:13px; margin:0 0 8px;">
                                        Atau copy link berikut ke browser kamu:
                                    </p>
                                    <p style="background:#F3F4F6; padding:12px;
                                              border-radius:4px; word-break:break-all;
                                              font-size:12px; color:#4B5563;">
                                        {verify_url}
                                    </p>

                                    <p style="color:#9CA3AF; font-size:12px; margin:16px 0 0;">
                                        ⚠️ Link ini hanya berlaku selama <strong>1 jam</strong>.
                                        Jika kamu tidak merasa mendaftar, abaikan email ini.
                                    </p>
                                </td>
                            </tr>

                            <!-- FOOTER -->
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
            subject="✉️ Verifikasi Email Anda — Commerce App",
            message=f"Verifikasi akun kamu: {verify_url}",  # fallback plain text
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,   # ← ini yang render HTML
            fail_silently=False,
        )

    except Exception as exc:
        raise self.retry(exc=exc)