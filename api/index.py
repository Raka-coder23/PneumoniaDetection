import os

def handler(request):
    """Serve the main HTML page"""
    try:
        # Read the HTML template
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'index.html')

        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': html_content
        }

    except FileNotFoundError:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': '<h1>Template not found</h1>'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': f'<h1>Error: {str(e)}</h1>'
        }