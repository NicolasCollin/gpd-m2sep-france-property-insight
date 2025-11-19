import gradio as gr


def get_home_page() -> tuple[gr.Button, gr.Button, gr.Button]:
    """
    Return Gradio components for the Home Page.

    Returns:
        tuple containing:
            - dashboard_card (gr.Button)
            - estimation_card (gr.Button)
            - about_card (gr.Button)
    """
    with gr.Blocks():
        with gr.Column(elem_id="home-container"):
            # Hero Section
            with gr.Row(elem_id="hero-section", scale=1):
                with gr.Column(elem_id="hero-content"):
                    _ = gr.HTML("""
                        <div class="hero-section">
                            <div class="hero-text-container">
                                <h1 class="hero-title">
                                    <span class="text-fixed">France Property Insight</span>
                                </h1>
                                <p class="hero-subtitle">
                                    <span class="text-rotating">
                                        <span class="word">unlock real estate intelligence</span>
                                        <span class="word">discover market insights</span>
                                        <span class="word">analyze property trends</span>
                                        <span class="word">predict property values</span>
                                        <span class="word">explore market data</span>
                                        <span class="word">master real estate analytics</span>
                                    </span>
                                </p>
                            </div>
                            <div class="hero-stats">
                                <div class="stat-item">
                                    <div class="stat-number">+2M</div>
                                    <div class="stat-label">Properties Analyzed</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number">96%</div>
                                    <div class="stat-label">Accuracy Rate</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number">2024</div>
                                    <div class="stat-label">Updated Data</div>
                                </div>
                            </div>
                        </div>
                        """)

            with gr.Row(elem_id="features-section"):
                with gr.Column():
                    _ = gr.Markdown("## Our features", elem_classes="feature-title")
                    with gr.Row():
                        dashboard_card: gr.Button = gr.Button(
                            "📊 DASHBOARD\n\nVisualize market trends, price per m², time evolution and detailed analysis by area",
                            elem_id="feature-dashboard",
                            elem_classes="feature-card",
                        )
                        estimation_card: gr.Button = gr.Button(
                            "🏠 ESTIMATION\n\nGet accurate property valuation thanks to our artificial intelligence models",
                            elem_id="feature-estimation",
                            elem_classes="feature-card",
                        )
                        about_card: gr.Button = gr.Button(
                            "ℹ️ ABOUT US\n\nDiscover our mission and expertise in French real estate market analysis",
                            elem_id="feature-about",
                            elem_classes="feature-card",
                        )

    return dashboard_card, estimation_card, about_card
