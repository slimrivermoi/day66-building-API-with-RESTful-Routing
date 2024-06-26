from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    ### Add to dictionary first
    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    """return a random cafe record in json format"""
    all_cafe = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
    random_cafe = random.choice(all_cafe)
    return jsonify(cafe=random_cafe.to_dict())
    ### This is a traditional way but it is very tedious if you have a huge DB to convert to json file.
    ### Instead of doing this, you should convert the content in the DB into a dictionary (see to_dict in class Cafe)
    ### then in this function, you just have to use one line to jsonify the dictionary
    # return jsonify(cafe={
    #     # Omit the id from the response
    #     # "id": random_cafe.id,
    #     "name": random_cafe.name,
    #     "map_url": random_cafe.map_url,
    #     "img_url": random_cafe.img_url,
    #     "location": random_cafe.location,
    #
    #     # Put some properties in a sub-category
    #     "amenities": {
    #         "seats": random_cafe.seats,
    #         "has_toilet": random_cafe.has_toilet,
    #         "has_wifi": random_cafe.has_wifi,
    #         "has_sockets": random_cafe.has_sockets,
    #         "can_take_calls": random_cafe.can_take_calls,
    #         "coffee_price": random_cafe.coffee_price,
    #     }
    # })


@app.route("/all")
def get_all_cafe():
    """return all records in the database in json format"""
    all_cafe = db.session.execute(db.select(Cafe).order_by(Cafe.id)).scalars().all()
    return jsonify(cafe=[cafe.to_dict() for cafe in all_cafe])

@app.route("/search")
def search_by_location():
    """search cafe by cafe ID"""
    query_location = request.args.get('loc')
    #this can get more than 1 cafe, this is why we use scalars, not scalar.
    all_cafe = db.session.execute(db.select(Cafe).where(Cafe.location == query_location)).scalars().all()
    if all_cafe:
        return jsonify(cafe=[cafe.to_dict() for cafe in all_cafe])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add_new_cafe():
    """add new cafe based on the form information"""
    new_cafe = Cafe(name=request.form.get('name'),
                    map_url=request.form.get('map_url'),
                    img_url=request.form.get('img_url'),
                    location=request.form.get('location'),
                    has_sockets=bool(request.form.get('has_sockets')),
                    has_toilet=bool(request.form.get('has_toilet')),
                    has_wifi=bool(request.form.get('has_wifi')),
                    can_take_calls=bool(request.form.get('can_take_calls')),
                    seats=request.form.get('seats'),
                    coffee_price=request.form.get('coffee_price'),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    """update coffee price of the cafe based on cafe id"""
    new_price = request.args.get('new_price')
    cafe_to_update = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=['DELETE'])
def delete_cafe(cafe_id):
    """delete a cafe entry based on cafe ID and API key"""
    auth_key = request.args.get('api_key')
    cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if auth_key == 'abcdefg':
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(deleted={"success": "Successfully deleted the cafe."})
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})
    else:
        return jsonify(error={"Sorry that's not allowed. Make sure you have the correct api_key."})


if __name__ == '__main__':
    app.run(debug=True, port=8080)
    # app.run(host='0.0.0.0', port=3000)
