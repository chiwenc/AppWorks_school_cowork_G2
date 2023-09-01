function clean_dom(dom) {
    while (dom.firstChild) {
        dom.removeChild(dom.firstChild)
    }
}

function append_product_dom(product_dom, product) {
    product_name = document.createElement("p")
    product_name.innerText = product.title
    product_name.style.fontSize = "x-large";
    product_link = document.createElement("a");
    product_link.href = "https://www.amazon.com/dp/" + product.id
    product_link.target = "_blank"
    product_link.rel = "noopener noreferrer"
    product_image = document.createElement("img")
    product_image.src = product.image_base64
    product_link.appendChild(product_image)
    product_dom.appendChild(product_name)
    product_dom.appendChild(product_link)
}

function show_product(product) {
    product_dom = document.getElementById('product')
    clean_dom(product_dom)
    title = document.createElement("h1")
    title.innerText = "Choosen Product"
    product_dom.appendChild(title)
    append_product_dom(product_dom, product)
}

function show_recommented_products(products) {
    product_dom = document.getElementById('recommend_products')
    clean_dom(product_dom)
    title = document.createElement("h1")
    title.innerText = "Recommended Products"
    console.log(title)
    product_dom.appendChild(title)
    console.log(product_dom)
    for (product of products) {
        append_product_dom(product_dom, product)
    }
}

async function show(item_id) {
    console.log(item_id)
    const product = await Promise.resolve($.ajax('/api/1.0/products/details?id=' + item_id))
    console.log(product)
    show_product(product.data)

    const recommended_products = await Promise.resolve($.ajax('/api/1.0/products/recommend?id=' + item_id))
    console.log(recommended_products)
    show_recommented_products(recommended_products.data)
}