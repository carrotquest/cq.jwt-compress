ARG PYTHON_VER=3.9

FROM python:${PYTHON_VER}-slim  AS image_stage

ARG APP_PATH=.

ENV APP_UID ${APP_UID:-1000}
ENV APP_GID ${APP_GID:-1000}
ENV APP_NAME ${APP_NAME:-"app"}

# Configure utf-8 locales to make sure Python correctly handles unicode filenames
# Configure pip local path to copy data from pip_stage
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 DJANGO_SETTINGS_MODULE=tests.settings PYTHONUSERBASE=/${APP_NAME}/pip PATH=/${APP_NAME}/pip/bin:$PATH

RUN set -eu && \
  groupadd --gid "${APP_GID}" "${APP_NAME}" && \
  useradd --uid ${APP_UID} --gid ${APP_GID} --create-home --shell /bin/bash -d /${APP_NAME} ${APP_NAME} && \
  chown -R ${APP_UID}:${APP_GID} /${APP_NAME}

USER ${APP_UID}
WORKDIR /${APP_NAME}/src

COPY ${APP_PATH} /${APP_NAME}/src

CMD ["python", "runtests.py"]
