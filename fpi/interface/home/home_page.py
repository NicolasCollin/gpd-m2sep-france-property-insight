import gradio as gr


def get_home_page() -> tuple[gr.Dropdown, gr.Button, gr.Button, gr.Button, gr.Button]:
    """
    Return Gradio components for the Home Page.

    Returns:
        tuple containing:
            - department_dropdown (gr.Dropdown)
            - search_button (gr.Button)
            - dashboard_card (gr.Button)
            - estimation_card (gr.Button)
            - about_card (gr.Button)
    """
    with gr.Blocks():
        with gr.Column(elem_id="home-container"):
            # Hero Section
            with gr.Row(elem_id="hero-section"):
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

            # Search section
            with gr.Row(elem_id="search-section"):
                with gr.Column(elem_id="search-container"):
                    _ = gr.HTML('<h2 class="search-title">All about a department</h2>')

                    with gr.Row(elem_id="search-input-row"):
                        department_dropdown: gr.Dropdown = gr.Dropdown(
                            label="Search a department (ex: 75, Paris)",
                            choices=[
                                "75 - Paris",
                                "77 - Seine-et-Marne",
                                "78 - Yvelines",
                                "91 - Essonne",
                                "92 - Hauts-de-Seine",
                                "93 - Seine-Saint-Denis",
                                "94 - Val-de-Marne",
                                "95 - Val-d'Oise",
                            ],
                            filterable=True,
                            interactive=True,
                            elem_id="department-search",
                        )
                        search_button: gr.Button = gr.Button("Analyze →", elem_id="search-button")

            # Features Section
            with gr.Row(elem_id="features-section"):
                with gr.Column():
                    _ = gr.HTML('<h2 class="features-title">Our features</h2>')
                    with gr.Row():
                        dashboard_card: gr.Button = gr.Button(
                            "📊 DASHBOARD\nVisualize market trends, price per m², time evolution and detailed analysis by area",
                            elem_id="feature-dashboard",
                            elem_classes="feature-card",
                        )
                        estimation_card: gr.Button = gr.Button(
                            "🏠 ESTIMATION\nGet accurate property valuation thanks to our artificial intelligence models",
                            elem_id="feature-estimation",
                            elem_classes="feature-card",
                        )
                        about_card: gr.Button = gr.Button(
                            "ABOUT US\nDiscover our mission and expertise in French real estate market analysis",
                            elem_id="feature-about",
                            elem_classes="feature-card",
                        )

    return department_dropdown, search_button, dashboard_card, estimation_card, about_card
