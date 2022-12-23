# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import os
import base64

import logging
logger = logging.getLogger(__name__)


def get_image(file_path):
    if os.path.isfile(file_path):
        f = open(file_path, 'rb')
        image_content_byte = f.read()
        f.close()
    return image_content_byte

class ImportPhotosProducts(models.Model):
    _name = "import.photos_products"
    _description = "Import photos product from reference"

    @api.model
    def import_photos_products(self):
        path_repo = self.env['ir.config_parameter'].get_param('photos_products_import_path')
        product_obj = self.env['product.product']
        logger.info(path_repo)

        os.chdir(path_repo)

        for file in os.listdir(path_repo):
            if str(file).lower().endswith('.jpg'):

                product_id = product_obj.search(
                    [('default_code', '=', str(file).split('.jpg')[0])])
                if product_id:
                    file_path = os.path.join(path_repo, file)
                    product_id.image_1920 = base64.encodebytes(get_image(file_path))


