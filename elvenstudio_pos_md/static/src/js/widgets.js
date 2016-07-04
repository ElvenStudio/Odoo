function elvenstudio_pos_md_widgets(instance, module) {

    var QWeb = instance.web.qweb,
    _t = instance.web._t;

    module.ProductListWidget = module.ProductListWidget.extend({

        // Rewrite the render_product function
        render_product: function(product){
            var cached = this.product_cache.get_node(product.id);
            if(!cached){
                var product_html = QWeb.render('Product',{
                        widget:  this,
                        product: product
                    });
                var product_node = document.createElement('div');
                product_node.innerHTML = product_html;
                product_node = product_node.childNodes[1];
                this.product_cache.cache_node(product.id,product_node);
                return product_node;
            }
            return cached;
        }
    });
}
