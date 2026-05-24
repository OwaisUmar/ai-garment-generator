import asyncio
import httpx

from config.settings import settings
from ui.screens.result_screen import render_result_screen


async def poll_job(
    container,
    job_id: str,
    generate_button,
    status_label,
    loader
):

    global is_generating

    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f'{settings.API_URL}/jobs/{job_id}')
            response.raise_for_status()
            result = response.json()
            status = result['status']
            
            # COMPLETED
            if status == 'completed':
                container.clear()
                render_result_screen(container, image_info=result)
                break

            # FAILED
            if status == 'failed':
                generate_button.enable()
                is_generating = False
                loader.visible = False
                status_label.set_content(
                    '''
                    <div class="text-center">
                        <div class="text-lg font-bold">
                            Generation failed.
                        </div>
                    </div>
                    '''
                )

                break

            # STILL PROCESSING
            await asyncio.sleep(3)