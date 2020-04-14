import dash_html_components as html
layout = html.Div([
    html.Pre([
        '尝试爬取一下',
        html.I(className='fa fa-bug'),
        html.Span(' '),
        html.A('https://v.douyin.com/3kCpYH/', href='javascript:void(0);', id='example-crawl'),
    ], className='website-info'),
    html.Div([
        html.Div(className='tile is-2'),
        html.Div([
            html.P([
                html.I(className='fa fa-question-circle'),
                '抖音用户链接来源说明'], className='has-text-primary is-size-4'),
            html.Div([
                html.Figure([
                    html.Img(src='/assets/picture/crawl_info1.jpg'),
                ], className='image crawl_img_info'),
                html.Figure([
                    html.Img(src='/assets/picture/crawl_info2.jpg'),
                ], className='image crawl_img_info'),
                html.Figure([
                    html.Img(src='/assets/picture/crawl_info3.jpg'),
                ], className='image crawl_img_info'),
            ], className='tile is-parent is-mobile'),
        ],className='tile is-vertical is-parent is-8')
    ], className='tile is-ancestor'),
], id='info_crawl')