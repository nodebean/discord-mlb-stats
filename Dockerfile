FROM python:3.12 as build

RUN apt-get update && apt-get install -y build-essential curl

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

ADD https://astral.sh/uv/install.sh /install.sh

RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh

COPY ./requirements.txt .

RUN /root/.local/bin/uv venv /opt/venv && \
    /root/.local/bin/uv pip install --no-cache -r requirements.txt


FROM python:3.12-slim-bookworm

COPY --from=build /opt/venv /opt/venv

COPY bot.py bot.py

USER nobody

ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT [ "python","bot.py" ]