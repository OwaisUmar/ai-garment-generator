from datetime import datetime
from pathlib import Path

import httpx
from nicegui import ui

from config.settings import settings

def render_result_screen(container, image_info):
    image_details = image_info['generation_details']
    
    with container:
        with ui.card().classes('w-full m-0 rounded-b-none border border-gray-300 shadow-none'):
            with ui.card_section():
                ui.html('<h6><strong style="color: #1e3a5f">Generation Result</strong></h6>')
        
        with ui.row().classes('w-full gap-0 items-stretch'):
            with ui.card().classes('w-1/2 m-0 rounded-none border border-gray-300 shadow-none'):
                with ui.row().classes('w-full justify-center'):
                    with ui.card_section():
                        ui.html('<strong class="w-full justify-center mb-2 text-base block">Generated Image</strong>')
                        with ui.row().classes('w-full justify-center'):
                            image_url = (
                                f'{settings.PUBLIC_API_URL}/'
                                f'{image_details["image_path"]}'
                            )
                            ui.image(image_url).classes(
                                '''
                                w-full
                                rounded
                                object-contain
                                '''
                            )

                            # Filename
                            generated_at = datetime.strptime(
                                image_details['generated_at'],
                                '%d %b %Y, %H:%M:%S'
                            )

                            image_filename = (
                                f'dress_output_'
                                f'{generated_at.strftime("%Y%m%d_%H%M%S")}.png'
                            )
                            ui.label(image_filename).classes(
                                'text-xs text-gray-500 text-center'
                            )

                            # Download button
                            with ui.row().classes(
                                'w-full justify-center mt-4 mb-2'
                            ):
                                download_button = ui.button(
                                    'Download Image',
                                    icon='download',
                                    on_click=lambda: ui.download(image_url, image_filename)
                                ).disable()
                            
            with ui.card().classes('w-1/2 m-0 rounded-none border border-gray-300 shadow-none'):
                with ui.row().classes('w-full justify-center'):
                    with ui.card_section():

                        ui.html('<strong class="w-full justify-center mb-5 text-base block">Generation Details</strong>')
                        # DETAILS BOX
                        with ui.card().classes(
                            'w-full justify-center border border-gray-300 shadow-none bg-gray-50'
                        ):

                            with ui.column().classes('w-full justify-center gap-2 p-2'):
                                details = [
                                    ('Garment Input', image_details['garment_input']),
                                    ('Color', image_details['color']),
                                    ('Fabric Input', image_details['fabric_input']),
                                    ('Image Size', image_details['image_size']),
                                    ('Quality', image_details['quality']),
                                    ('Generated At', image_details['generated_at']),
                                ]

                                for label, value in details:

                                    with ui.row().classes(
                                        'w-full justify-between items-center'
                                    ):

                                        ui.html(
                                            f'''
                                            <div
                                                style="
                                                    color: #6b7280;
                                                    font-weight: 600;
                                                    width: 180px;
                                                "
                                            >
                                                {label}
                                            </div>
                                            '''
                                        )

                                        ui.html(
                                            f'''
                                            <div
                                                style="
                                                    color: #1f2937;
                                                    text-align: left;
                                                    flex: 1;
                                                "
                                            >
                                                {value}
                                            </div>
                                            '''
                                        )

                        # =========================================================
                        # FEEDBACK SECTION
                        # =========================================================

                        ui.html(
                            '''
                            <div class="mt-6">
                                <div
                                    style="
                                        font-size: 22px;
                                        font-weight: 700;
                                        color: #1e3a5f;
                                    "
                                >
                                    How satisfied are you with this result?
                                </div>

                                <div
                                    style="
                                        color: #6b7280;
                                        font-style: italic;
                                        margin-top: 6px;
                                    "
                                >
                                    Please rate before saving. Your score helps us improve
                                    generation quality.
                                </div>
                            </div>
                            '''
                        )

                        # =========================================================
                        # STAR RATING
                        # =========================================================
                        with ui.row().classes('w-full justify-center'):
                            rating = ui.rating(value=0, max=5).props('size=2.5em color=orange').classes('mt-2')

                            rating.on_value_change(
                                lambda e:
                                rating_label.set_text(f'{e.value} out of 5')
                            )
                            
                            rating_label = ui.label('0 out of 5').classes('w-1/2 text-orange font-bold text-base m-3')

                        # =========================================================
                        # COMMENT BOX
                        # =========================================================

                        comment_input = ui.textarea(
                            label='Comments (optional)',
                            placeholder=('Tell us what you liked or what could be improved...')
                        ).props('outlined'
                        ).classes('w-full mt-4')

                        # =========================================================
                        # ACTION BUTTONS
                        # =========================================================

                        async def submit_feedback():
                            if not rating.value:
                                ui.notify(
                                    'Star rating is required before saving.',
                                    type='negative',
                                    position='top',
                                )
                                return
                            submit_feedback_button.disable()
                            submit_feedback_button.props('loading')
                            try:
                                async with httpx.AsyncClient() as client:
                                    response = await client.post(
                                        f'{settings.API_URL}/jobs/{image_info["job_id"]}/feedback',
                                        json={
                                            'rating': rating.value,
                                            'comment': comment_input.value,
                                        }
                                    )

                                    response.raise_for_status()

                                submit_feedback_button.set_text('Update Feedback')
                                download_button.enable()

                                ui.notify(
                                    'Feedback saved successfully.',
                                    type='positive',
                                    position='top',
                                )

                            except httpx.HTTPStatusError as exc:
                                submit_feedback_button.enable()
                                try:
                                    detail = exc.response.json()['detail']
                                except Exception:
                                    detail = exc.response.text

                                ui.notify(
                                    f'Failed to save feedback: {detail}',
                                    type='negative',
                                    position='top',
                                )

                            except Exception:
                                submit_feedback_button.enable()
                                ui.notify(
                                    'Unexpected error while saving feedback.',
                                    type='negative',
                                    position='top',
                                )
                            
                            finally:
                                submit_feedback_button.enable()
                                submit_feedback_button.props(remove='loading')

                        with ui.row().classes(
                            'w-full justify-between mt-6'
                        ):
                            def generate_again():
                                from ui.screens.generate_form import render_generation_form

                                polling_task = getattr(
                                    container,
                                    'polling_task',
                                    None,
                                )

                                if polling_task and not polling_task.done():
                                    polling_task.cancel()

                                container.clear()
                                render_generation_form(container)

                            submit_feedback_button = ui.button(
                                'Submit Feedback',
                                on_click=submit_feedback,
                            ).classes('w-[48%] bg-blue-600 text-white font-semibold')

                            ui.button(
                                'Generate Again',
                                on_click=generate_again
                            ).classes('w-[48%]'
                            ).props('outline')
                            