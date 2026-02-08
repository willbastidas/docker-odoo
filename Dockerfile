FROM odoo:17.0
USER root
RUN pip3 install python-dotenv
USER odoo
