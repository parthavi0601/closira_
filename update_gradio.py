import sys

with open('app/gradio_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_customer_tab = False
for i, line in enumerate(lines):
    if 'with gr.Row():' in line and i > 440 and i < 460 and not in_customer_tab:
        new_lines.append('    with gr.Tabs():\n')
        new_lines.append('        with gr.Tab("💬 Customer Interface"):\n')
        new_lines.append('        ' + line)
        in_customer_tab = True
    elif in_customer_tab and i <= 580:
        new_lines.append('        ' + line)
    else:
        new_lines.append(line)

admin_tab = """
        with gr.Tab("🛡️ Admin Dashboard & Logs"):
            gr.Markdown("## 🚨 Escalations & Out-of-SOP Questions")
            refresh_btn = gr.Button("🔄 Refresh Logs", variant="secondary")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Escalations Log (`logs/escalations.log`)")
                    escalations_view = gr.Textbox(lines=25, show_label=False, interactive=False)
                with gr.Column():
                    gr.Markdown("### Summaries Log (`logs/summaries.md`)")
                    summaries_view = gr.Textbox(lines=25, show_label=False, interactive=False)
            
            def load_logs():
                import os
                esc_log = "No escalations logged yet."
                sum_log = "No summaries logged yet."
                if os.path.exists("logs/escalations.log"):
                    with open("logs/escalations.log", "r", encoding="utf-8") as f:
                        esc_log = f.read()
                if os.path.exists("logs/summaries.md"):
                    with open("logs/summaries.md", "r", encoding="utf-8") as f:
                        sum_log = f.read()
                return esc_log, sum_log
            
            refresh_btn.click(fn=load_logs, inputs=[], outputs=[escalations_view, summaries_view])
"""

new_lines.insert(581, admin_tab)

with open('app/gradio_app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
