# products
import os

# Get absolute path to images directory
images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images'))

products = [
    {
        "name" : "Cabe Merah Ori",
        "price" : 21000,
        "image" : os.path.join(images_dir, "1.jpg"),
        "description" : "Cabe Merah Ori per kilogram",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Merah Keriting",
        "price" : 28000,
        "image" : os.path.join(images_dir, "3.jpg"),
        "description" : "Cabe Merah keriting per kilogram",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Hijau Keriting",
        "price" : 16000,
        "image" : os.path.join(images_dir, "2.jpg"),
        "description" : "Cabe Hijau Keriting per kilogram",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Rawit Merah",
        "price" : 19000,
        "image" : os.path.join(images_dir, "5.jpg"),
        "description" : "Cabe Rawit Merah per kilogram",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Rawit Hijau",
        "price" : 10000,
        "image" : os.path.join(images_dir, "4.jpg"),
        "description" : "Cabe Rawit Hijau per kilogram",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Rawit Putih",
        "price" : 11000,
        "image" : os.path.join(images_dir, "6.jpg"),
        "description" : "Cabe Rawit Putih per Kilogram",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
]