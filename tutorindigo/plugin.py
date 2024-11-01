from __future__ import annotations

import os
import typing as t

import importlib_resources
from tutor import hooks, utils
from tutor.__about__ import __version_suffix__

from .__about__ import __version__

# Handle version suffix in nightly mode, just like tutor core
if __version_suffix__:
    __version__ += "-" + __version_suffix__


################# Configuration
config: t.Dict[str, t.Dict[str, t.Any]] = {
    # Add here your new settings
    "defaults": {
        "VERSION": __version__,
        "WELCOME_MESSAGE": "Welcome to the Aspen Courses",
        "COMPANY_NAME": "Aspen Publishing",
        "ENABLE_DARK_THEME": False,
        "PRIMARY_COLOR": "#bf2d2e",  # Indigo
        "SHOW_UNAUTHENTICATED_NAVBAR": False,
        # Footer links are dictionaries with a "title" and "url"
        # To remove all links, run:
        # tutor config save --set INDIGO_FOOTER_NAV_LINKS=[]
        "FOOTER_NAV_LINKS": [
            {"title": "About Us", "url": "https://aspenpublishing.com/pages/discover-jd-next-program"},
            {"title": "Support", "url": "https://support.aspenpublishing.com/hc/en-us/categories/19204583377428-JD-Next"},
            {"title": "End User License Agreement", "url": "/agreement"},
            {"title": "Terms Of Use", "url": "/tos"},
            {"title": "Privacy Statement", "url": "/privacy"},
            {"title": "California Disclosure", "url": "/disclosure"},
        ],
        "FOOTER_SOCIAL_LINKS": [
            {"title": "x", "url": "https://twitter.com/AspenPublishing"},
            {"title": "linkedin", "url": "https://www.linkedin.com/company/aspenpublishing/"},
            {"title": "youtube", "url": "https://www.youtube.com/@aspenpublishing6830"},
            {"title": "facebook", "url": "https://www.facebook.com/profile.php?id=61555997104704"},
        ],
    },
    "unique": {},
    "overrides": {},
}

# Theme templates
hooks.Filters.ENV_TEMPLATE_ROOTS.add_item(
    (str(importlib_resources.files("tutorindigo") / "templates"))
)

# This is where the theme is rendered in the openedx build directory
hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    [
        ("indigo", "build/openedx/themes"),
        ("indigo/env.config.jsx", "plugins/mfe/build/mfe"),
    ],
)

# Force the rendering of scss files, even though they are included in a "partials" directory
hooks.Filters.ENV_PATTERNS_INCLUDE.add_items(
    [
        r"indigo/lms/static/sass/partials/lms/theme/",
        r"indigo/cms/static/sass/partials/cms/theme/",
    ]
)


# init script: set theme automatically
with open(
    os.path.join(
        str(importlib_resources.files("tutorindigo") / "templates"),
        "indigo",
        "tasks",
        "init.sh",
    ),
    encoding="utf-8",
) as task_file:
    hooks.Filters.CLI_DO_INIT_TASKS.add_item(("lms", task_file.read()))


# Override openedx & mfe docker image names
@hooks.Filters.CONFIG_DEFAULTS.add(priority=hooks.priorities.LOW)
def _override_openedx_docker_image(
    items: list[tuple[str, t.Any]]
) -> list[tuple[str, t.Any]]:
    openedx_image = ""
    mfe_image = ""
    for k, v in items:
        if k == "DOCKER_IMAGE_OPENEDX":
            openedx_image = v
        elif k == "MFE_DOCKER_IMAGE":
            mfe_image = v
    if openedx_image:
        items.append(("DOCKER_IMAGE_OPENEDX", f"{openedx_image}-indigo"))
    if mfe_image:
        items.append(("MFE_DOCKER_IMAGE", f"{mfe_image}-indigo"))
    return items


# Load all configuration entries
hooks.Filters.CONFIG_DEFAULTS.add_items(
    [(f"INDIGO_{key}", value) for key, value in config["defaults"].items()]
)
hooks.Filters.CONFIG_UNIQUE.add_items(
    [(f"INDIGO_{key}", value) for key, value in config["unique"].items()]
)
hooks.Filters.CONFIG_OVERRIDES.add_items(list(config["overrides"].items()))


hooks.Filters.ENV_PATCHES.add_items(
    [
        # MFE will install header version 3.0.x and will include indigo-footer as a
        # separate package for use in env.config.jsx
        (
            "mfe-dockerfile-post-npm-install-learning",
            """
RUN npm install '@edx/brand@git+https://github.com/AspenPublishing/Aspen.Courses.brand-openedx.git#dacf789577f1b64f647d0c290f731245508c53c2'
RUN npm install '@edx/frontend-component-header@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-header#c317c859bdf79a3299b845a71504a14deb26311d'
RUN npm install '@edx/frontend-component-footer@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-footer#fb86690e42d9b21c4730aafeafa341f7cf3775cf'

COPY indigo/env.config.jsx /openedx/app/
""",
        ),
        (
            "mfe-dockerfile-post-npm-install-authn",
            """
RUN npm install '@edx/brand@git+https://github.com/AspenPublishing/Aspen.Courses.brand-openedx.git#dacf789577f1b64f647d0c290f731245508c53c2'
""",
        ),
        # Tutor-Indigo v2.1 targets the styling updates in discussions and learner-dashboard MFE
        # brand-openedx is related to styling updates while others are for header and footer updates
        (
            "mfe-dockerfile-post-npm-install-discussions",
            """
RUN npm install '@edx/brand@git+https://github.com/AspenPublishing/Aspen.Courses.brand-openedx.git#dacf789577f1b64f647d0c290f731245508c53c2'
RUN npm install '@edx/frontend-component-header@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-header#c317c859bdf79a3299b845a71504a14deb26311d'
RUN npm install '@edx/frontend-component-footer@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-footer#fb86690e42d9b21c4730aafeafa341f7cf3775cf'

COPY indigo/env.config.jsx /openedx/app/
""",
        ),
        (
            "mfe-dockerfile-post-npm-install-learner-dashboard",
            """
RUN npm install '@edx/brand@git+https://github.com/AspenPublishing/Aspen.Courses.brand-openedx.git#dacf789577f1b64f647d0c290f731245508c53c2'
RUN npm install '@edx/frontend-component-header@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-header#c317c859bdf79a3299b845a71504a14deb26311d'
RUN npm install '@edx/frontend-component-footer@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-footer#fb86690e42d9b21c4730aafeafa341f7cf3775cf'

COPY indigo/env.config.jsx /openedx/app/
""",
        ),
        (
            "mfe-dockerfile-post-npm-install-profile",
            """
RUN npm install '@edx/brand@git+https://github.com/AspenPublishing/Aspen.Courses.brand-openedx.git#dacf789577f1b64f647d0c290f731245508c53c2'
RUN npm install '@edx/frontend-component-header@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-header#c317c859bdf79a3299b845a71504a14deb26311d'
RUN npm install '@edx/frontend-component-footer@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-footer#fb86690e42d9b21c4730aafeafa341f7cf3775cf'

COPY indigo/env.config.jsx /openedx/app/
""",
        ),
        (
            "mfe-dockerfile-post-npm-install-account",
            """
RUN npm install '@edx/brand@git+https://github.com/AspenPublishing/Aspen.Courses.brand-openedx.git#dacf789577f1b64f647d0c290f731245508c53c2'
RUN npm install '@edx/frontend-component-header@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-header#c317c859bdf79a3299b845a71504a14deb26311d'
RUN npm install '@edx/frontend-component-footer@git+https://github.com/AspenPublishing/Aspen.Courses.frontend-component-footer#fb86690e42d9b21c4730aafeafa341f7cf3775cf'

COPY indigo/env.config.jsx /openedx/app/
""",
        ),
    ]
)

# Include js file in lms main.html, main_django.html, and certificate.html

hooks.Filters.ENV_PATCHES.add_items(
    [
        # for production
        (
            "openedx-common-assets-settings",
            """
javascript_files = ['base_application', 'application', 'certificates_wv']
dark_theme_filepath = ['indigo/js/dark-theme.js']

for filename in javascript_files:
    if filename in PIPELINE['JAVASCRIPT']:
        PIPELINE['JAVASCRIPT'][filename]['source_filenames'] += dark_theme_filepath
  
""",
        ),
        # for development
        (
            "openedx-lms-development-settings",
            """
javascript_files = ['base_application', 'application', 'certificates_wv']
dark_theme_filepath = ['indigo/js/dark-theme.js']

for filename in javascript_files:
    if filename in PIPELINE['JAVASCRIPT']:
        PIPELINE['JAVASCRIPT'][filename]['source_filenames'] += dark_theme_filepath
""",
        ),
    ]
)