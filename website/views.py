from importlib.metadata import metadata
from random import vonmisesvariate
from flask import Blueprint, render_template, request, redirect, url_for
from requests import RequestException
import stripe
from .models import Cinemahall, Movie, Qrcode, Show, User, Booking, Showseat
from . import db
import random

views = Blueprint('views', __name__)
stripe.api_key = 'sk_test_51LLwkYKKfRH6nq6FYChFWFAS1AtNd1FcwNEF8gDFoZeCLUHmU1QnPu3MeAq58cKgPPs1xNBRRJd0Gg1nhhbl5URs00lfFe36AX'
YOUR_DOMAIN = 'https://moviesriobravo.herokuapp.com'
# QA 'http://127.0.0.1:5000'
# PROD https://moviesriobravo.herokuapp.com

# This function will run whenever we go to the route defined above
@views.route('/')
def home():
    movies = Movie.query.order_by(Movie.id)
    shows = Show.query.order_by(Show.time)
    return render_template("home.html", movies=movies, shows=shows)

@views.route('/compra/<int:id>')
def compra(id):
    show_of_movie = Show.query.get_or_404(id)
    movie_to_display = Movie.query.get_or_404(show_of_movie.movie_id)
    return render_template("compra.html", movie=movie_to_display, show=show_of_movie)

@views.route('/asientos.html/<int:id>', methods=["GET"])
def asientos(id):
    if request.method == "GET":
        show_of_movie = Show.query.get_or_404(id)
        movie_to_display = Movie.query.get_or_404(show_of_movie.movie_id)
        showseats = Showseat.query.filter_by(show_id=show_of_movie.id).all()

        qty_tickets = request.args.get('qty tickets')
        qty_adulto = request.args.get('qty adulto')
        qty_senior = request.args.get('qty senior')
        qty_child = request.args.get('qty child')
        total_price = request.args.get('total-price')
        return render_template("asientos.html",movie=movie_to_display, show=show_of_movie, showseats=showseats, qty_tickets=qty_tickets, qty_adulto=qty_adulto, qty_senior=qty_senior, qty_child=qty_child, total_price=total_price)

@views.route('/create-checkout-session', methods=["POST"])
def checkout():
    if request.method == 'POST':
        qty_adulto = request.form.get('qty adulto')
        qty_senior = request.form.get('qty senior')
        qty_child = request.form.get('qty child')
        total_tickets = int(qty_adulto) + int(qty_child) + int(qty_senior)

        seats_list = request.form.get('what-seats-vertical')

        show_id = request.form.get('show_id')
        
        arrQty = [qty_adulto, qty_senior, qty_child]
        arrPrice = ['price_1LMDfqKKfRH6nq6FBId7Uyfl', 'price_1LMDgDKKfRH6nq6FHgDxUCUc', 'price_1LMDgXKKfRH6nq6FQsSOydfu']
        line_items = []

        for i in range(3):
            if(arrQty[i] != '0'):
                line_items.append({'price': arrPrice[i], 'quantity': arrQty[i]})

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                success_url= YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url= YOUR_DOMAIN + '/home.html',
                metadata={
                    'total_tickets' : total_tickets,
                    'seats_list' : seats_list,
                    'show_id' : show_id
                }
            )
        except Exception as e:
            return str(e)

    return redirect(checkout_session.url, code=303)

@views.route('/success', methods=['GET'])
def success():
    if request.method == 'GET':
        try:
            session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
            #line_items = stripe.checkout.Session.list_line_items(request.args.get('session_id'))
            customer = stripe.Customer.retrieve(session.customer)

            email = request.form.get(customer.email)
            new_user = User(email=email)
            db.session.add(new_user)
            db.session.commit()

            show_id = session.metadata['show_id']
            new_booking = Booking(number_seats=session.metadata['total_tickets'],show_id=show_id)
            db.session.add(new_booking)
            db.session.commit()

            seats_string = session.metadata['seats_list']
            seats_list = seats_string.split(",")
            for seat in seats_list:
                showseat = Showseat.query.filter_by(show_id=new_booking.show_id,seat=seat).first()
                showseat.status = 1
                db.session.commit()
            
            show_of_movie = Show.query.get_or_404(show_id)
            movie_to_display = Movie.query.get_or_404(show_of_movie.movie_id)

            random_number = random.randint(7777,80000)
            qr_code = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + str(show_of_movie.movie_id) + str(show_id) + str(show_of_movie.cinemahall_id) + seats_string + str(random_number)

            qrcodedb = Qrcode(code_message=qr_code,isscanned=0,user_id=new_user.id)
            db.session.add(qrcodedb)
            db.session.commit()

        except Exception as e:
            return str(e)

        return render_template("success.html", session=session, show_of_movie=show_of_movie, movie=movie_to_display, customer=customer, qr_code=qr_code)

@views.route('/admin.html', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # To add one movie at a time in Movie table
        movie_name = request.form.get('name')
        movie_image = request.form.get('image')
        genre = request.form.get('genre')
        duration = request.form.get('duration') + ' min'

        try:
            new_movie = Movie(name=movie_name,image=movie_image,genre=genre,duration=duration)
            db.session.add(new_movie)
            db.session.commit()

            # To add shows for that movie in specific
            num_sala = request.form.get('numsala')
            hora_peli = request.form.get('horapeli')
            
            sala = Cinemahall.query.filter_by(hall_number=num_sala).first()
            show_numbers = request.form.get('number-of-shows')

            new_show = Show(time=hora_peli, movie_id=new_movie.id, cinemahall_id=sala.id)
            db.session.add(new_show)
            db.session.commit()

            letter_columns = ['A','B','C','D','E','F','G','H','I']
            number_row = ['1','2','3','4','5','6','7','8','9','10','11','12']
            # Add 108 records (108 seats) for each show
            for i in letter_columns:
                for j in number_row:
                    new_showseat = Showseat(status=0,seat=i+j,show_id=new_show.id)
                    db.session.add(new_showseat)
                    db.session.commit()

            for i in range(int(show_numbers)-1):
                num_sala = request.form.get('numsala'+str(i))
                hora_peli = request.form.get('horapeli'+str(i))

                sala = Cinemahall.query.filter_by(hall_number=num_sala).first()

                new_show = Show(time=hora_peli, movie_id=new_movie.id, cinemahall_id=sala.id)
                db.session.add(new_show)
                db.session.commit()

                # Add 108 records (108 seats) for each show
                for i in letter_columns:
                    for j in number_row:
                        new_showseat = Showseat(status=0,seat=i+j,show_id=new_show.id)
                        db.session.add(new_showseat)
                        db.session.commit()

        except Exception as e:
            return str(e)

        return redirect('/admin.html')

    else:
        movies = Movie.query.order_by(Movie.id)
        shows = Show.query.order_by(Show.id)
        return render_template('admin.html', movies=movies, shows=shows)

@views.route('/delete/<int:id>')
def delete(id):
    movie_to_delete = Movie.query.get_or_404(id)
    shows_to_delete = Show.query.filter_by(movie_id=id).all()
    try:
        db.session.delete(movie_to_delete)
        db.session.commit()
        for show in shows_to_delete:
            db.session.delete(show)
            db.session.commit()
        return redirect('/admin.html')
    except:
        return "There was an error deleting this movie"

@views.route('/deleteshow/<int:id>')
def deleteshow(id):
    show_to_delete = Show.query.get_or_404(id)

    try:
        db.session.delete(show_to_delete)
        db.session.commit()
        return redirect('/admin.html')
    except:
        return "There was an error deleting this movie"

@views.route('/deletehall/<int:id>')
def deletehall(id):
    hall_to_delete = Cinemahall.query.get_or_404(id)

    try:
        db.session.delete(hall_to_delete)
        db.session.commit()
        return redirect('/addSalas.html')
    except:
        return "There was an error deleting this hall"

@views.route('addSalas.html', methods=['GET', 'POST'])
def salas():
    if request.method == 'POST':
        numero_sala = request.form.get('numero-sala')
        seats_no = request.form.get('seatsno')

        try:
            new_sala = Cinemahall(hall_number=numero_sala,total_seats=seats_no)
            db.session.add(new_sala)
            db.session.commit()
        except Exception as e:
            return str(e)

        return redirect('/addSalas.html')

    else:
        salas = Cinemahall.query.order_by(Cinemahall.id)
        return render_template('addSalas.html', salas=salas)

@views.route('main_movie_shows.html')
def main_movie_shows():
    movie = Movie.query.filter_by(id=4).first()
    return render_template('main_movie_shows.html', movie=movie)

@views.route('qr_scanner.html')
def qr_scanner():
    qrcode_list = Qrcode.query.order_by(Qrcode.id)
    return render_template('qr_scanner.html', qrcode_list=qrcode_list)

@views.route('scan_result.html/<string:message>')
def scan_result(message):
    prefix = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data='
    message = prefix + message
    qrcode = Qrcode.query.filter_by(code_message=message).first()
    qrcodes = Qrcode.query.order_by(Qrcode.id)
    if qrcode:
        exists = 1
    else:
        exists = 0
    return render_template('scan_result.html', exists=exists, qrcodes=qrcodes)

@views.route('precios.html')
def precios():
    return render_template('precios.html')

@views.route('/updatemovie/<int:id>', methods=['GET', 'POST'])
def update_movie(id):
    movie = Movie.query.get_or_404(id)
    if request.method == 'POST':
        movie.name = request.form.get('name')
        movie.image = request.form.get('image')
        movie.genre = request.form.get('genre')
        movie.duration = request.form.get('duration')

        try:
            db.session.commit()
            return redirect('/admin.html')
        except:
            return 'There was an error updating the movie'
    else:
        return render_template('updatemovie.html', movie=movie)

@views.route('/addshow/<int:id>', methods=['GET','POST'])
def add_show(id):
    movie = Movie.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # To add shows for that movie in specific
            num_sala = request.form.get('numsala')
            hora_peli = request.form.get('horapeli')
            
            sala = Cinemahall.query.filter_by(hall_number=num_sala).first()
            show_numbers = request.form.get('number-of-shows')

            new_show = Show(time=hora_peli, movie_id=id, cinemahall_id=sala.id)
            db.session.add(new_show)
            db.session.commit()

            letter_columns = ['A','B','C','D','E','F','G','H','I']
            number_row = ['1','2','3','4','5','6','7','8','9','10','11','12']
            # Add 108 records (108 seats) for each show
            for i in letter_columns:
                for j in number_row:
                    new_showseat = Showseat(status=0,seat=i+j,show_id=new_show.id)
                    db.session.add(new_showseat)
                    db.session.commit()

            for i in range(int(show_numbers)-1):
                num_sala = request.form.get('numsala'+str(i))
                hora_peli = request.form.get('horapeli'+str(i))

                sala = Cinemahall.query.filter_by(hall_number=num_sala).first()

                new_show = Show(time=hora_peli, movie_id=id, cinemahall_id=sala.id)
                db.session.add(new_show)
                db.session.commit()

                # Add 108 records (108 seats) for each show
                for i in letter_columns:
                    for j in number_row:
                        new_showseat = Showseat(status=0,seat=i+j,show_id=new_show.id)
                        db.session.add(new_showseat)
                        db.session.commit()
            return redirect('/admin.html')

        except Exception as e:
            return str(e)
    else:
        return render_template('addshow.html', movie=movie)
