import asyncio
import httpx

from nicegui import ui

from config.settings import settings
from ui.polling import poll_job


async def submit_generation(
    *,
    container,
    data: dict,
    files: dict,
    generate_button,
    status_label,
    loader
):

    try:
        generate_button.disable()
        loader.visible = True
        status_label.set_content(
            '''
            <div class="text-center">
                <div class="text-lg font-bold">
                    Generating your image...
                </div>

                <div class="text-sm italic text-gray-500">
                    This usually takes 30–60 seconds. Please wait and do not refresh the page.
                </div>
            </div>
            '''
        )

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                f'{settings.API_URL}/generate',
                data=data,
                files=files,
            )

            response.raise_for_status()
            result = response.json()
            job_id = result['job_id']

            asyncio.create_task(
                poll_job(
                    container=container,
                    job_id=job_id,
                    generate_button=generate_button,
                    status_label=status_label,
                    loader=loader
                )
            )

    except httpx.HTTPStatusError as exc:
        generate_button.enable()
        try:
            detail = exc.response.json().get(
                'detail',
                exc.response.text,
            )
        except Exception:
            detail = exc.response.text

        status_label.set_content('')
        ui.notify(
            f'Generation failed: {detail}',
            type='negative',
            position='top',
        )

    except httpx.TimeoutException:
        generate_button.enable()
        status_label.set_content('')
        ui.notify(
            'Request timed out.',
            type='negative',
            position='top',
        )

    except Exception as exc:
        generate_button.enable()
        status_label.set_content('')
        ui.notify(
            f'Unexpected error. {exc}',
            type='negative',
            position='top',
        )
        raise