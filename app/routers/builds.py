from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.lib.database_api import get_entries, get_entry_by_id

router = APIRouter()

def error_page(message: str) -> str:
    return f"""
    <html>
        <head>
            <title>Error</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }}
                .error-box {{
                    background-color: #ffebee;
                    border: 1px solid #ffcdd2;
                    border-radius: 5px;
                    padding: 20px;
                    margin: 20px;
                    max-width: 600px;
                }}
                .back-link {{
                    margin-top: 20px;
                }}
                .back-link a {{
                    color: #0066cc;
                    text-decoration: none;
                }}
                .back-link a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="error-box">
                <h2>Error</h2>
                <p>{message}</p>
            </div>
            <div class="back-link">
                <a href="/builds">← Back to Build List</a>
            </div>
        </body>
    </html>
    """

@router.get("/builds", response_class=HTMLResponse)
async def get_builds():
    builds = get_entries()
    
    if isinstance(builds, dict) and "error" in builds:
        return HTMLResponse(content=error_page(builds["error"]), status_code=500)
    
    if not builds:
        return HTMLResponse(content=error_page("No builds found in the database."), status_code=404)
    
    html_content = """
    <html>
        <head>
            <title>CI Build History</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .build-list { list-style: none; padding: 0; }
                .build-item { 
                    margin: 10px 0;
                    padding: 15px;
                    background-color: #f5f5f5;
                    border-radius: 5px;
                }
                .build-item a {
                    color: #0066cc;
                    text-decoration: none;
                }
                .build-item a:hover {
                    text-decoration: underline;
                }
                .branch-tag {
                    display: inline-block;
                    background-color: #e1e4e8;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.9em;
                    margin-left: 8px;
                }
            </style>
        </head>
        <body>
            <h1>CI Build History</h1>
            <ul class="build-list">
    """
    
    for build in builds:
        build_id = build[0]
        commit_hash = build[1]
        branch = build[2]
        date = build[3]
        html_content += f"""
                <li class="build-item">
                    <a href="/builds/{build_id}">
                        Build #{build_id} - Commit: {commit_hash} - Date: {date}
                    </a>
                    <span class="branch-tag">{branch}</span>
                </li>
        """
    
    html_content += """
            </ul>
        </body>
    </html>
    """
    return html_content

@router.get("/builds/{build_id}", response_class=HTMLResponse)
async def get_build(build_id: str):
    try:
        build_id_int = int(build_id)
    except ValueError:
        return HTMLResponse(
            content=error_page("Invalid build ID format. Must be a number."),
            status_code=400
        )
    
    build = get_entry_by_id(build_id_int)
    
    if isinstance(build, dict) and "error" in build:
        return HTMLResponse(content=error_page(build["error"]), status_code=500)
    
    if not build or len(build) == 0:
        return HTMLResponse(
            content=error_page(f"Build #{build_id} not found."),
            status_code=404
        )
    
    build = build[0]
    commit_hash = build[1]
    branch = build[2]
    date = build[3]
    test_syntax_result = build[4]
    test_notifier_result = build[5]
    test_CI_result = build[6]
    test_syntax_log = build[7]
    test_notifier_log = build[8]
    test_CI_log = build[9]
    
    html_content = f"""
    <html>
        <head>
            <title>Build #{build_id} Details</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .back-link {{ margin-bottom: 20px; }}
                .back-link a {{ color: #0066cc; text-decoration: none; }}
                .back-link a:hover {{ text-decoration: underline; }}
                .build-details {{ 
                    background-color: #f5f5f5;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .branch-tag {{
                    display: inline-block;
                    background-color: #e1e4e8;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.9em;
                    margin-left: 8px;
                }}
                .test-section {{
                    margin-top: 20px;
                    padding: 15px;
                    border-radius: 5px;
                }}
                .test-section.success {{
                    background-color: #e8f5e9;
                    border: 1px solid #c8e6c9;
                }}
                .test-section.failure {{
                    background-color: #ffebee;
                    border: 1px solid #ffcdd2;
                }}
                .test-section.error {{
                    background-color: #fff3e0;
                    border: 1px solid #ffe0b2;
                }}
                .test-log {{
                    background-color: #2b2b2b;
                    color: #ffffff;
                    padding: 15px;
                    border-radius: 5px;
                    white-space: pre-wrap;
                    font-family: monospace;
                    margin-top: 10px;
                    max-height: 400px;
                    overflow-y: auto;
                }}
            </style>
        </head>
        <body>
            <div class="back-link">
                <a href="/builds">← Back to Build List</a>
            </div>
            <div class="build-details">
                <h1>Build #{build_id}</h1>
                <p>
                    <strong>Commit Hash:</strong> {commit_hash}
                    <span class="branch-tag">{branch}</span>
                </p>
                <p><strong>Build Date:</strong> {date}</p>
            </div>
            
            <div class="test-section {test_syntax_result}">
                <h2>Syntax Test Results</h2>
                <p><strong>Status:</strong> {test_syntax_result}</p>
                <div class="test-log">
                    {test_syntax_log}
                </div>
            </div>
            
            <div class="test-section {test_notifier_result}">
                <h2>Notifier Test Results</h2>
                <p><strong>Status:</strong> {test_notifier_result}</p>
                <div class="test-log">
                    {test_notifier_log}
                </div>
            </div>
            
            <div class="test-section {test_CI_result}">
                <h2>CI Test Results</h2>
                <p><strong>Status:</strong> {test_CI_result}</p>
                <div class="test-log">
                    {test_CI_log}
                </div>
            </div>
        </body>
    </html>
    """
    return html_content

