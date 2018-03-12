###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
import json
import requests

## App setup code
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.config['SECRET_KEY'] = 'pokemonpokemon'
## All app.config values
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/Midterm-katmazan"
## Provided:
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################




##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    height_value = db.Column(db.Integer, db.ForeignKey('heights.id'))
    weight_value = db.Column(db.Integer, db.ForeignKey('weights.id'))
    def __repr__(self):
        return ('{' + str(self.name) + '} | ID: {' + str(self.id) + '}')
class Height(db.Model):
    __tablename__ = 'heights'
    id = db.Column(db.Integer, primary_key=True)
    poke_height = db.Column(db.Integer)
    poke_name = db.Column(db.String)
    names = db.relationship('Name',backref='Height')

class Weight(db.Model):
    __tablename__ = 'weights'
    id = db.Column(db.Integer,primary_key=True)
    poke_name = db.Column(db.String)
    poke_weight = db.Column(db.Integer)
    names = db.relationship('Name',backref='Weight')
###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    name = StringField("Pokemon_name",validators=[Required()])
    submit = SubmitField()
    def validate_name(self, field):
        if len(field.data) <= 1:
            raise ValidationError('Pokemon does not exist')

class FavoriteForm(FlaskForm):
    fav_name = StringField("Add one of your favorite Pokemon:")
    nick_name = StringField("Give your favorite a nickname:")
    submit = SubmitField()
    def validate_nick_name(self,field):
        if field.data[-1] != 'y':
            raise ValidationError("Your nickname must end in y!")
class RankForm(FlaskForm):
    name = StringField('Enter a Pokemon name:', validators = [Required()])
    rate = RadioField('Rate this pokemon in terms of how powerful you think it is', choices = [('1', '1 (low)'), ('2', '2'), ('3', '3 (high)')])
    submit = SubmitField('Submit')




#######################
###### VIEW FXNS ######
#######################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_error.html'), 404

@app.route('/', methods = ['GET', 'POST'])
def home():
    form = NameForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
    
    if form.validate_on_submit():
        poke_name = form.name.data
        pokemon = Name.query.filter_by(name=poke_name).first()
        ##only adds pokemon if it is not in database
        if not pokemon:
            
           
        
        
            params = {}
            params['name'] = str(poke_name)
        
            print(params)
            
            response = requests.get('http://pokeapi.co/api/v2/pokemon/' + params['name'] + '/')
            ##if response.status_code != '200':
                ##return("The data you entered was not available in the data, check spelling")
            
        
            poke_height = int(json.loads(response.text)['height'])
            new_height = Height(poke_height = poke_height, poke_name = poke_name)
            db.session.add(new_height)
            db.session.commit()
        
            poke_weight = int(json.loads(response.text)['weight'])
            new_weight = Weight(poke_weight = poke_weight, poke_name = poke_name)
            db.session.add(new_weight)
            db.session.commit()
            print('hello')
            
            newname = Name(name = poke_name, height_value = new_height.id, weight_value = new_weight.id)
            db.session.add(newname)
            db.session.commit()

            return redirect(url_for('all_names'))
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('base.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)

@app.route('/tallest')
def tallest_pokemon():
    all_heights = Height.query.all()
    tallest_pokemon = 0
    for h in all_heights:
        height = h.poke_height
        if height > tallest_pokemon:
            tallest_pokemon = height
            tp = h
    tallest = tp.poke_name
    height = tp.poke_height

    return render_template('tallest_pokemon.html', tallest = tallest, height = height, names = all_heights)

@app.route('/heaviest')
def heaviest_pokemon():
    all_weights = Weight.query.all()
    heaviest_pokemon = 0
    for w in all_weights:
        weight = w.poke_weight
        if weight > heaviest_pokemon:
            heaviest_pokemon = weight
            hp = w
    heaviest = hp.poke_name
    weight = hp.poke_weight

    return render_template('heaviest.html', heaviest = heaviest, weight = weight, names = all_weights)

@app.route('/favorite_pokemon')
def favorite_form():
    form = FavoriteForm()
    return render_template('favorite_form.html', form = form)

@app.route('/fav_answers',methods=["GET","POST"])
def show_favs():
    form = FavoriteForm()
    if request.args:
        fav_name = form.fav_name.data
        nickname = form.nick_name.data
        
        return render_template('fav_results.html',fav_name=fav_name, nick_name=nickname)

    flash(form.errors)
    return redirect(url_for('favorite_form'))


## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
