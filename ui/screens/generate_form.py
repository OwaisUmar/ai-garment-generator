import re

from nicegui import ui

from ui.generation import submit_generation
from ui.utils.colors import hex_to_name


def render_generation_form(container):

    garment_text_input = None
    fabric_text_input = None
    color_input = None

    garment_file = {'file': None}
    color_file = {'file': None}
    fabric_file = {'file': None}
    
    status_label = None

    loader = None
    generate_button = None

    with container:
        with ui.card().classes('w-full m-0 rounded-b-none border border-gray-300 shadow-none'):
            with ui.card_section():
                ui.html('<h6><strong style="color: #1e3a5f">Generate Garment</strong></h6>')
                ui.html('<p style="color: gray;"><i>Provide the garment design, color, and fabric to generate a photorealistic product image.</i></p>')
        
        with ui.row().classes('w-full gap-0 items-stretch'):
            with ui.card().classes('w-1/3 m-0 rounded-none border border-gray-300 shadow-none'):
                with ui.card_section():
                    ui.html('<strong class="mb-1 block">1. Garment Design</strong>')
                    ui.html('<p style="color: gray;" class="text-xs"><b>How would you like to specify the garment?</b></p>')
                    garment_radio = ui.radio(['Upload Image', 'Text Description'], value="Upload Image").props('inline').classes("text-xs mt-2")

                    dynamic_garment_container = ui.row().classes('w-full mt-3')
                    
                    def update_garment_upload():
                        nonlocal garment_text_input
                        dynamic_garment_container.clear()
                        garment_text_input = None
                        garment_file['file'] = None

                        with dynamic_garment_container:
                            if garment_radio.value == 'Upload Image':
                                def on_garment_upload(e):
                                    garment_file['file'] = e.file
                                    ui.notify(f'Uploaded {e.file.name}', position='top')
                                ui.upload(
                                    label='Garment Sketch / Reference Image (PNG / JPG / WEBP — max 10MB)', 
                                    on_upload=on_garment_upload,
                                    on_rejected=lambda: ui.notify(
                                        'Upload failed. Please select a PNG, JPG, JPEG, or WEBP image no larger than 10 MB.',
                                        type='negative',
                                        position='top'
                                    ),
                                    auto_upload=True,
                                    max_file_size=10_000_000).classes('max-w-full').props(
                                        'accept=".png,.jpg,.jpeg,.webp"'
                                    )
                            else:
                                garment_text_input = ui.input(
                                    placeholder='e.g. Sherwani, Kurta, A-line dress...',
                                    validation={
                                        'Please enter a garment description.': lambda v: bool(v and v.strip()),
                                        'Description must be at least 3 characters long.': lambda v: len(v.strip()) >= 3 if v else False,
                                        'Description must be 200 characters or fewer.': lambda v: len(v.strip()) <= 200 if v else True,
                                    }
                                ).props('outlined dense').classes('w-full text-xs text-gray bg-gray-100 p-0')
                                
                    update_garment_upload()
                    garment_radio.on_value_change(lambda _: update_garment_upload())

            with ui.card().classes('w-1/3 m-0 rounded-none border border-gray-300 shadow-none'):
                with ui.card_section():
                    ui.html('<strong class="mb-1 block">2. Color</strong>')
                    ui.html('<p style="color: gray;" class="text-xs"><b>How would you like to specify the color?</b></p>')
                    color_radio = ui.radio(['Color Picker', 'Color Image'], value='Color Picker').props('inline').classes('text-xs mt-2')

                    dynamic_color_container = ui.row().classes('w-full mt-3')
                    
                    def update_color_upload():
                        nonlocal color_input
                        dynamic_color_container.clear()
                        color_input = None
                        
                        with dynamic_color_container:
                            if color_radio.value == 'Color Picker':
                                
                                
                                hex_color = '#FF0000'
                                with ui.row().classes('w-full'):
                                    preview = ui.html(f'<div class="w-10 h-10 mt-3 rounded" style="background-color: {hex_color}"></div>')
                                    def update_preview():
                                        preview.set_content(f'<div class="w-10 h-10 mt-3 rounded border border-gray-300" style="background-color: {color_input.value}"></div>')

                                    color_input = ui.color_input(label="Pick Color", 
                                                                placeholder='Or enter hex code', 
                                                                value=hex_color,
                                                                on_change=update_preview,
                                                                preview=True
                                                            )
                                
                                color_label = ui.html(f'<div style="color: {hex_color}">{hex_to_name(hex_color)}</div>')
                                color_input.on_value_change(lambda _: color_label.set_content(f'<div style="color: {color_input.value}">{hex_to_name(color_input.value)}</div>'))
                                    
                            else:
                                def on_color_upload(e):
                                    color_file['file'] = e.file
                                    ui.notify(f'Uploaded {e.file.name}', position='top')
                                    
                                ui.upload(
                                    label='Upload a color reference image (PNG / JPG / WEBP — max 10MB)', 
                                    on_upload=on_color_upload,
                                    on_rejected=lambda: ui.notify(
                                        'Upload failed. Please select a PNG, JPG, JPEG, or WEBP image no larger than 10 MB.',
                                        type='negative',
                                        position='top'
                                    ),
                                    auto_upload=True,
                                    max_file_size=10_000_000).classes('max-w-full').props(
                                        'accept=".png,.jpg,.jpeg,.webp"'
                                    )
                                
                    update_color_upload()
                    color_radio.on_value_change(lambda _: update_color_upload())

            with ui.card().classes('w-1/3 m-0 rounded-none border border-gray-300 shadow-none'):
                with ui.card_section():
                    ui.html('<strong class="mb-1 block">3. Fabric / Material</strong>')
                    ui.html('<p style="color: gray;" class="text-xs"><b>How would you like to specify the fabric?</b></p>')
                    fabric_radio = ui.radio(['Upload Image', 'Text Description'], value="Upload Image").props('inline').classes("text-xs mt-2")

                    dynamic_fabric_container = ui.row().classes('w-full mt-3')
                    
                    def update_fabric_upload():
                        nonlocal fabric_text_input
                        dynamic_fabric_container.clear()
                        fabric_text_input = None
                        
                        with dynamic_fabric_container:
                            if fabric_radio.value == 'Upload Image':
                                def on_fabric_upload(e):
                                    fabric_file['file'] = e.file
                                    ui.notify(f'Uploaded {e.file.name}', position='top')
                                    
                                ui.upload(
                                    label='Fabric Swatch / Reference Image (PNG / JPG / WEBP — max 10MB)', 
                                    on_upload=on_fabric_upload,
                                    on_rejected=lambda: ui.notify(
                                        'Upload failed. Please select a PNG, JPG, JPEG, or WEBP image no larger than 10 MB.',
                                        type='negative',
                                        position='top'
                                    ),
                                    auto_upload=True,
                                    max_file_size=10_000_000).classes('max-w-full').props(
                                        'accept=".png,.jpg,.jpeg,.webp"'
                                    )
                            else:
                                fabric_text_input = ui.input(
                                    placeholder='e.g. silk, cotton, brocade, linen...',
                                    validation={
                                        'Please enter a fabric description.': lambda v: bool(v and v.strip()),
                                        'Description must be at least 3 characters long.': lambda v: len(v.strip()) >= 3 if v else False,
                                        'Description must be 200 characters or fewer.': lambda v: len(v.strip()) <= 200 if v else True,
                                    }
                                ).props('outlined dense').classes('w-full text-xs text-gray bg-gray-100 p-0')
                                
                    update_fabric_upload()
                    fabric_radio.on_value_change(lambda _: update_fabric_upload())

        async def generate_image():
            data = {}
            files = {}
            
            if garment_radio.value == 'Upload Image':
                if garment_file['file'] is None:
                    ui.notify('Please upload a design image before generating.', color='negative', position='top')
                    return
                file_bytes = await garment_file['file'].read()
                files['garment_image'] = (garment_file['file'].name, file_bytes, garment_file['file'].content_type)
            else:
                if garment_text_input is None or not garment_text_input.validate():
                    ui.notify('Please fix the garment description errors before generating.', color='negative', position='top')
                    return
                data['garment_text'] = garment_text_input.value.strip()

            if color_radio.value == 'Color Picker':
                if color_input is None or not re.fullmatch(
                    r'#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})',
                    color_input.value.strip()
                ):
                    ui.notify('Enter valid hex code before generating.', color='negative', position='top')
                    return
                data['color_text'] = hex_to_name(color_input.value)
            else:
                if color_file['file'] is None:
                    ui.notify('Please upload a color image before generating', color='negative', position='top')
                    return
                file_bytes = await color_file['file'].read()
                files['color_image'] = (color_file['file'].name, file_bytes, color_file['file'].content_type)
                    
            if fabric_radio.value == 'Upload Image':
                if fabric_file['file'] is None:
                    ui.notify('Please upload a fabric image before generating.', color='negative', position='top')
                    return
                file_bytes = await fabric_file['file'].read()
                files['fabric_image'] = (fabric_file['file'].name, file_bytes, fabric_file['file'].content_type)
            else:
                if fabric_text_input is None or not fabric_text_input.validate():
                    ui.notify('Please fix the fabric description errors before generating.', color='negative', position='top')
                    return
                data['fabric_text'] = fabric_text_input.value.strip()

            # Submit generation
            await submit_generation(
                container=container,
                data=data,
                files=files,
                generate_button=generate_button,
                status_label=status_label,
                loader=loader
            )
            
        with ui.column().classes("w-full m-0 pb-20 rounded-t-none border border-gray-300 shadow-none"):
            with ui.row().classes("w-full justify-center mt-10"):
                generate_button = ui.button('Generate Image').on_click(generate_image)
            
            with ui.row().classes("w-full justify-center"):
                loader = ui.spinner('dots', size='lg')
                loader.visible = False
            
            with ui.row().classes("w-full justify-center"):
                status_label = ui.html()
