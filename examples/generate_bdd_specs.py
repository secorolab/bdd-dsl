import sys
from os.path import join, dirname
from timeit import default_timer as timer
from urllib.request import HTTPError
import rdflib

from rdf_utils.uri import URL_SECORO_M
from rdf_utils.resolver import install_resolver
from rdf_utils.naming import get_valid_filename
from bdd_dsl.models.user_story import UserStoryLoader
from bdd_dsl.utils.jinja import (
    load_template_from_url,
    prepare_jinja2_template_data,
)
from bdd_dsl.models.frames import FR_NAME


PKG_ROOT = join(dirname(__file__), "..")
GENERATED_DIR = join(PKG_ROOT, "examples", "generated")
MODEL_URLS = {
    f"{URL_SECORO_M}/acceptance-criteria/bdd/environments/secorolab.env.json": "json-ld",
    f"{URL_SECORO_M}/acceptance-criteria/bdd/agents/isaac-sim.agn.json": "json-ld",
    f"{URL_SECORO_M}/acceptance-criteria/bdd/scenes/secorolab-env.scene.json": "json-ld",
    f"{URL_SECORO_M}/acceptance-criteria/bdd/scenes/isaac-agents.scene.json": "json-ld",
    # f"{URL_SECORO_M}/acceptance-criteria/bdd/templates/pickplace.tmpl.json": "json-ld",
    f"{URL_SECORO_M}/acceptance-criteria/bdd/templates/sorting.tmpl.json": "json-ld",
    # f"{URL_SECORO_M}/acceptance-criteria/bdd/pickplace-secorolab-isaac.var.json": "json-ld",
    f"{URL_SECORO_M}/acceptance-criteria/bdd/sorting-secorolab-isaac.var.json": "json-ld",
}


def main():
    # By default, istall custom resolver that download files to user's cache directory
    # This resolver is used by rdflib to load remote resources, e.g. included as URLs in the context.
    install_resolver()

    g = rdflib.Dataset()
    for url, fmt in MODEL_URLS.items():
        g.parse(url, format=fmt)

    start = timer()
    try:
        us_loader = UserStoryLoader(g)
    except HTTPError as e:
        print(f"error loading models URL '{e.url}':\n{e.info()}\n{e}")
        sys.exit(1)

    end = timer()
    print(f"UserStoryLoader init time: {end - start:.5f} seconds")

    start = timer()
    processed_bdd_data = prepare_jinja2_template_data(us_loader, g)
    end = timer()
    print(f"Jinja template data preparation time: {end - start:.5f} seconds")

    feature_template = load_template_from_url(
        f"{URL_SECORO_M}/acceptance-criteria/bdd/jinja/feature.jinja"
    )
    for us_data in processed_bdd_data:
        us_name = us_data[FR_NAME]
        feature_content = feature_template.render(data=us_data)
        feature_filename = f"{get_valid_filename(us_name)}.feature"
        filepath = join(GENERATED_DIR, feature_filename)
        with open(filepath, mode="w", encoding="utf-8") as of:
            of.write(feature_content)
            print(f"... wrote {filepath}")


if __name__ == "__main__":
    main()
