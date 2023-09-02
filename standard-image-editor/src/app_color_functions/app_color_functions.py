# packages
import sys
import time
import tracemalloc
from flask import Flask, request, g
from flask_lambda import FlaskLambda
from flask_swagger_ui import get_swaggerui_blueprint

sys.path.append('../..')

# local
from src.common import common_functions as common, file_manager as fm
from handlers import (
    handler_color_codes,
    handler_rgb_channels,
    handler_rgb_histograms
)

# app_convert_functions flask
if fm.get_configuration() == "LOCAL":
    common.log("Local FLASK")
    app = Flask(__name__)
else:
    common.log("Lambda FLASK")
    app = FlaskLambda(__name__)


@app.before_request
def setup_procedure():
    # memory
    if request.headers.get("Memory-Test") == "True":
        tracemalloc.start()
    # time
    g.start_time = time.perf_counter()


@app.after_request
def teardown_procedure(response):
    # time
    total_time = time.perf_counter() - g.start_time
    time_in_ms = int(total_time * 1000)
    common.log('Request took {} seconds (milliseconds: {}) {} {}'
               .format(total_time, time_in_ms, request.method, request.path))
    response.headers['total_time'] = total_time
    # memory
    if request.headers.get("Memory-Test") == "True":
        memory_current, memory_peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        response.headers['memory_spike'] = memory_peak - memory_current
        response.headers['memory_peak'] = memory_peak
    return response


# app_color_functions swagger
SWAGGER_URL = '/swagger-color'
API_URL = '/static/swagger_color.json'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "app_color_functions"})

app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix=SWAGGER_URL)


# get profiling decorator
conditional_profiling = common.get_conditional_profiling()


# routes
@app.route('/color-codes-text', methods=['POST'])
@conditional_profiling
def post_create_color_codes_text() -> tuple:
    common.log(post_create_color_codes_text.__name__)
    mandatory_parameters = ["images_paths"]
    optional_parameters = {"occurrence_threshold": 500}

    for mandatory_parameter in mandatory_parameters:
        if mandatory_parameter not in request.json:
            return common.respond_bad_request_missing(mandatory_parameter)

    images_paths = request.json["images_paths"]

    for optional_parameter in list(optional_parameters.keys()):
        if optional_parameter in request.json:
            optional_parameters[optional_parameter] = request.json[optional_parameter]

    return handler_color_codes.handle_post_color_codes_text(images_paths, optional_parameters)


@app.route('/color-codes-chart', methods=['POST'])
@conditional_profiling
def post_create_color_codes_chart() -> tuple:
    common.log(post_create_color_codes_chart.__name__)
    mandatory_parameters = ["images_paths"]
    optional_parameters = {"occurrence_threshold": 500}

    for mandatory_parameter in mandatory_parameters:
        if mandatory_parameter not in request.json:
            return common.respond_bad_request_missing(mandatory_parameter)

    images_paths = request.json["images_paths"]

    for optional_parameter in list(optional_parameters.keys()):
        if optional_parameter in request.json:
            optional_parameters[optional_parameter] = request.json[optional_parameter]

    return handler_color_codes.handle_post_color_codes_chart(images_paths, optional_parameters)


@app.route('/rgb-channels', methods=['POST'])
@conditional_profiling
def post_create_rgb_channels() -> tuple:
    common.log(post_create_rgb_channels.__name__)
    mandatory_parameters = ["images_paths"]
    optional_parameters = {"greyscale_flag": False}

    for mandatory_parameter in mandatory_parameters:
        if mandatory_parameter not in request.json:
            return common.respond_bad_request_missing(mandatory_parameter)

    images_paths = request.json["images_paths"]

    for optional_parameter in list(optional_parameters.keys()):
        if optional_parameter in request.json:
            optional_parameters[optional_parameter] = request.json[optional_parameter]

    return handler_rgb_channels.handle_post_rgb_channels(images_paths, optional_parameters)


@app.route('/rgb-histogram', methods=['POST'])
@conditional_profiling
def post_create_rgb_histograms() -> tuple:
    common.log(post_create_rgb_histograms.__name__)
    mandatory_parameters = ["images_paths"]

    for mandatory_parameter in mandatory_parameters:
        if mandatory_parameter not in request.json:
            return common.respond_bad_request_missing(mandatory_parameter)

    images_paths = request.json["images_paths"]

    return handler_rgb_histograms.handle_post_rgb_histograms(images_paths)


if __name__ == '__main__':
    common.check_bucket()
    app.run(host="0.0.0.0", debug=True, port=8000)
