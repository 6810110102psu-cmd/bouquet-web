from app import app, db, Flower

with app.app_context():
    flowers = [
        Flower(name="Lily of the Valley", image="images/flowers/1.png"),
        Flower(name="White Rose", image="images/flowers/2.png"),
        Flower(name="Dusty Purple Rose", image="images/flowers/3.png"),
        Flower(name="Waxflower", image="images/flowers/4.png"),
        Flower(name="Carnation", image="images/flowers/5.png"),
        Flower(name="Gerbera", image="images/flowers/6.png"),
        Flower(name="Hydrangea", image="images/flowers/7.png"),
        Flower(name="Tulip", image="images/flowers/8.png"),
        Flower(name="Hyacinth", image="images/flowers/9.png"),
        Flower(name="Calla Lily", image="images/flowers/10.png"),
        Flower(name="Phalaenopsis Orchid", image="images/flowers/11.png"),
        Flower(name="Marigold", image="images/flowers/12.png"),
        Flower(name="Daisy",image="images/flowers/13.png"),
        Flower(name="Anthurium", image="images/flowers/14.png"),
        Flower(name="Sunflower", image="images/flowers/15.png"),
        Flower(name="Aster", image="images/flowers/16.png"),
        Flower(name="Gypsophila", image="images/flowers/17.png"),
        Flower(name="Lily", image="images/flowers/18.png"),
        Flower(name="Eucalyptus", image="images/flowers/19.png"),
    ]

    db.session.add_all(flowers)
    db.session.commit()
    
    print("Seed flowers completed!")
    
    if Flower.query.first():
        print("Flowers already seeded")
        exit()