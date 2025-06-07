# products
import os

# Get absolute path to images directory
images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images'))

products = [
    {
        "name" : "Cabe Merah Ori",
        "price" : 21000,
        "image" : os.path.join(images_dir, "1.jpg"),
        "description" : "Cabe Merah Ori per kilogram. Cabai merah besar dengan warna cerah dan rasa pedas sedang. Cocok untuk berbagai masakan seperti sambal, balado, dan tumisan. Segar, harum, dan berkualitas super.",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Merah Keriting",
        "price" : 28000,
        "image" : os.path.join(images_dir, "3.jpg"),
        "description" : "Cabe Merah keriting per kilogram. Cabai merah ramping dengan tekstur keriting dan warna merah menyala. Rasa pedasnya lebih kuat, cocok untuk sambal ulek atau masakan pedas favorit. Tersedia dalam kondisi segar dan siap olah.",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Hijau Keriting",
        "price" : 16000,
        "image" : os.path.join(images_dir, "2.jpg"),
        "description" : "Cabe Hijau Keriting per kilogram. Cabai hijau keriting dengan aroma segar dan rasa pedas khas. Cocok untuk tumisan, sambal ijo, atau lalapan. Warna hijau alami dan tekstur renyah saat digigit.",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Rawit Merah",
        "price" : 19000,
        "image" : os.path.join(images_dir, "5.jpg"),
        "description" : "Cabe Rawit Merah per kilogram. Cabai kecil dengan warna merah cerah dan tingkat kepedasan tinggi. Favorit untuk pecinta sambal ekstrem. Tahan lama, segar, dan bikin masakan makin nendang.",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Rawit Hijau",
        "price" : 10000,
        "image" : os.path.join(images_dir, "4.jpg"),
        "description" : "Cabe Rawit Hijau per kilogram. Cabai rawit hijau dengan rasa pedas kuat dan aroma khas. Ukuran kecil, cocok untuk pelengkap gorengan, sambal mentah, atau masakan sehari-hari. Selalu segar setiap kiriman.",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
    {
        "name" : "Cabe Rawit Putih",
        "price" : 11000,
        "image" : os.path.join(images_dir, "6.jpg"),
        "description" : "Cabe Rawit Putih per Kilogram. Cabai rawit putih dengan warna krem muda dan rasa pedas menyengat. Jarang ditemukan, cocok untuk sambal khas daerah atau penggemar pedas ekstrem. Segar, unik, dan siap kirim.",
        "category" : "Vegetables",
        "featured" : True,
        "in stock" : True,
    },
]