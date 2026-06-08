import os
import gradio as gr
from groq import Groq

# ── Anup Rao's profile baked in as the system context ──────────────────────
SYSTEM_PROMPT = """You are a professional AI assistant representing Anup Rao's career profile.
Your job is to help recruiters and hiring managers learn about Anup's experience, skills, and fit for open roles.
Be concise, confident, and professional. Highlight strengths naturally.
If asked something not covered below, say you don't have that detail but invite them to reach out directly at Raonoops@gmail.com or via LinkedIn at linkedin.com/in/raoanup.
Do not make up any information — only use what is provided here.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANUP RAO — CAREER PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SUMMARY:
Associate Product Manager with 8+ years spanning product, engineering, and operations.
Most recently drove the roadmap for internal ad-serving and campaign validation systems at X (Twitter),
a role he held from May 2024 through April 2026. Now actively seeking his next opportunity.
Over the past 2 months he has been upskilling in Java, Spring Boot, and backend engineering,
and sharpening his DSA fundamentals through LeetCode. He is open to both Senior PM roles and
Backend Developer / Software Engineer roles. Technical background in React, Node.js, platform
engineering, and enterprise ops gives him an unusually hands-on lens. Comfortable in both 0-to-1
and scale contexts, with a track record of improving system throughput, client satisfaction, and
cross-functional delivery.

CONTACT:
- Email: Raonoops@gmail.com
- LinkedIn: https://www.linkedin.com/in/raoanup
- Location: Ontario, Canada
- Open to remote: Yes | Open to relocation: No

TARGET ROLES: Senior Product Manager, Technical PM, Backend Developer, Backend Engineer, Software Engineer
TARGET INDUSTRIES: AdTech, SaaS, Developer Tools, E-Commerce, FinTech, Media

━━━ EXPERIENCE ━━━

1. Associate Product Manager — X (Previously Twitter) | May 2024 – Apr 2026
   - Owned roadmap for internal ad-serving and campaign validation systems
   - Improved campaign throughput by 18% via data-driven backlog prioritization using Datadog & Grafana
   - Monitored KPIs: impression latency, campaign success rate
   - Partnered with engineering, design, and ad operations across global teams
   - NOTE: Anup is no longer at X as of April 2026 and is actively seeking new PM opportunities

2. Associate Product Manager — Artohlam Group Inc. | Sep 2023 – Apr 2024
   - Wrote PRDs for truck check-in automation improving client satisfaction and retention
   - Managed end-to-end API rollout coordinating design, QA, and customer onboarding
   - Balanced operational scalability with client-driven feature priorities

3. Frontend Solutions Developer — Webtrigon | May 2021 – Jul 2022
   - Built React UI components and web forms integrating REST APIs
   - Developed the Packages Bundle + Save conversion flow
   - Led client onboarding workshops and created training materials

4. Platform Developer — Scaler (E-Learning) | Apr 2020 – Apr 2021
   - Built features for a platform supporting 15,000+ career transformations
   - Served 900+ placement partners with zero unplanned downtime during scaling
   - Designed RESTful APIs bridging web and mobile platforms

5. Enterprise Operations Analyst — Accenture | Dec 2018 – Mar 2020
   - SAP ecosystem: ABAP, SAPUI5, SAP HANA
   - Improved vendor invoice workflow efficiency by 15% via automation and pattern recognition

6. Quality Analyst — Pole to Win | Mar 2016 – Nov 2018
   - Developed and executed test plans for PlayStation and Xbox game titles
   - Operated in controlled sandbox environments for hardware and software validation

━━━ EDUCATION ━━━
- M.S. Computer Science — Algoma University, Ontario, Canada (2024)
- B.S. Computer Science — Amity University, India (2015)

━━━ SKILLS ━━━
Product:     Roadmapping, PRD Writing, Agile, A/B Testing, User Research, GTM, Stakeholder Management
Analytics:   SQL, Datadog, Grafana, Prometheus, KPI Design
Engineering: Java (actively upskilling), Spring Boot (actively upskilling), DSA / LeetCode, React, JavaScript, Node.js, REST API, AWS, ABAP, SAPUI5, SAP HANA
Tools:       Jira, Confluence
Domain:      Advertising Technology, Cross-Functional Leadership

━━━ KEY ACHIEVEMENTS ━━━
- 18% campaign throughput improvement at X through data-driven backlog prioritization
- 15% reduction in vendor invoice cycle time at Accenture via SAP automation
- Scaled Scaler platform to 15,000+ learners and 900+ placement partners with no downtime
- End-to-end delivery of truck check-in automation at Artohlam, improving client retention
"""

# ── Groq client (free API — add GROQ_API_KEY as a Space secret) ─────────────
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def respond(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        if assistant_msg:
            messages.append({"role": "assistant", "content": assistant_msg})

    messages.append({"role": "user", "content": message})

    response = ""
    try:
        stream = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-8b-instant",
            max_tokens=512,
            stream=True,
            temperature=0.7,
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                response += token
                yield response
    except Exception as e:
        yield f"Sorry, I ran into an issue. Please try again or reach out to Anup directly at Raonoops@gmail.com. (Error: {str(e)})"

# ── Gradio UI ────────────────────────────────────────────────────────────────
_theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="slate",
    neutral_hue="slate",
    font=gr.themes.GoogleFont("Inter"),
)

_css = """
/* Remove fixed height from the empty chatbot area — let it grow with messages */
.chatbot-container, .chatbot, [data-testid="chatbot"] {
    min-height: 0 !important;
    height: auto !important;
}
.chatbot .wrap, .chatbot .bubble-wrap {
    min-height: 0 !important;
}
/* Tighten up the overall layout padding */
.gradio-container {
    padding-top: 12px !important;
}
footer { display: none !important; }
"""

with gr.Blocks(theme=_theme, css=_css, title="Ask About Anup Rao") as demo:
    gr.Markdown("## Ask About Anup Rao")
    gr.Markdown(
        "I'm an AI assistant loaded with Anup's full career profile. "
        "Ask me about his experience, skills, or fit for your role."
    )
    gr.ChatInterface(
        fn=respond,
        chatbot=gr.Chatbot(show_label=False),
        textbox=gr.Textbox(placeholder="Ask me anything about Anup…", container=False),
        submit_btn="Send",
    )

if __name__ == "__main__":
    demo.launch()
