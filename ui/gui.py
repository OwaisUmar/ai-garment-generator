from nicegui import ui

from ui.screens.generate_form import render_generation_form
from ui.screens.result_screen import render_result_screen

@ui.page('/')
def generate():
    main_container = ui.column().classes('w-full')
    
    with ui.header(elevated=False).style('background-color: #1e3a5f'):
        ui.html('<strong>Fashion Image Generator</strong>')
    render_generation_form(main_container)
        
# @ui.page('/result')
# def result():
#     main_container = ui.column().classes('w-full')
    
#     with ui.header(elevated=False).style('background-color: #1e3a5f'):
#         ui.html('<strong>Fashion Image Generator</strong>')
#     render_result_screen(main_container)
    
    
ui.run()