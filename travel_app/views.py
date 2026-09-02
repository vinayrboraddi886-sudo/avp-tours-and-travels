import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User, Destination, Package, Booking, Review

def ok(data, status=200):
    return JsonResponse({'success': True, 'data': data}, status=status)

def err(msg, status=400):
    return JsonResponse({'success': False, 'error': msg}, status=status)

@csrf_exempt
def login(request):
    if request.method != 'POST':
        return err('POST required', 405)
    try:
        body = json.loads(request.body)
        user = User.objects.get(
            email=body.get('email','').lower().strip(),
            password=body.get('password',''))
        return ok({'id': user.id, 'name': user.name,
                   'email': user.email, 'role': user.role})
    except User.DoesNotExist:
        return err('Invalid email or password', 401)

@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    try:
        body     = json.loads(request.body)
        name     = body.get('name', '').strip()
        email    = body.get('email', '').strip().lower()
        phone    = body.get('phone', '').strip()
        password = body.get('password', '')

        # ── Validate ──
        if not name or not email or not password:
            return JsonResponse({'success': False, 'error': 'Name, email and password are required'})

        if len(password) < 6:
            return JsonResponse({'success': False, 'error': 'Password must be at least 6 characters'})

        # ── Check if email already exists ──
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'This email is already registered. Please sign in.'})

        # ── Save new user to database ──
        user = User.objects.create(
            name     = name,
            email    = email,
            phone    = phone,
            password = password,
            role     = 'user'
        )

        return JsonResponse({
            'success' : True,
            'message' : 'Account created successfully',
            'data'    : {
                'id'    : user.id,
                'name'  : user.name,
                'email' : user.email,
                'role'  : user.role
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
def destinations(request):
    qs  = Destination.objects.filter(is_active=True)
    cat = request.GET.get('category','')
    if cat and cat != 'all':
        qs = qs.filter(category=cat)
    return ok([{
        'id': d.id,
        'destination_name': d.destination_name,
        'country': d.country,
        'description': d.description,
        'price_inr': float(d.price_inr),
        'price_usd': float(d.price_usd),
        'best_time': d.best_time,
        'duration_days': d.duration_days,
        'category': d.category,
        'image_url': d.image_url
    } for d in qs])

def packages(request):
    qs = Package.objects.filter(is_active=True).select_related('destination')
    return ok([{
        'id': p.id,
        'package_name': p.package_name,
        'destination_name': p.destination.destination_name if p.destination else '',
        'description': p.description,
        'price_inr': float(p.price_inr),
        'price_usd': float(p.price_usd),
        'duration_days': p.duration_days,
        'includes': p.includes,
        'image_url': p.image_url
    } for p in qs])

@csrf_exempt
def bookings(request):

    if request.method == 'GET':
        try:
            all_bookings = Booking.objects.all().order_by('id')
            data = []
            for b in all_bookings:
                data.append({
                    'id'              : b.id,
                    'full_name'       : getattr(b, 'full_name', '') or getattr(b, 'name', '') or '',
                    'email'           : getattr(b, 'email', '') or '',
                    'phone'           : getattr(b, 'phone', '') or '',
                    'destination'     : getattr(b, 'destination', '') or '',
                    'travel_date'     : str(b.travel_date) if getattr(b, 'travel_date', None) else '',
                    'people'          : getattr(b, 'people', '') or getattr(b, 'travelers', 1) or 1,
                    'budget_inr'      : str(getattr(b, 'budget_inr', '') or getattr(b, 'budget', 0) or 0),
                    'special_requests': getattr(b, 'special_requests', '') or getattr(b, 'notes', '') or '',
                    'status'          : getattr(b, 'status', 'pending') or 'pending',
                })
            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    elif request.method == 'POST':
        try:
            body   = json.loads(request.body)
            action = body.get('action', '')

            # ── UPDATE STATUS (admin confirm/cancel) ──
            if action == 'update_status':
                booking_id = body.get('id')
                new_status = body.get('status')

                if new_status not in ['pending', 'confirmed', 'cancelled']:
                    return JsonResponse({'success': False, 'error': 'Invalid status'})

                try:
                    booking        = Booking.objects.get(id=booking_id)
                    booking.status = new_status
                    booking.save()
                    return JsonResponse({
                        'success': True,
                        'message': f'Booking #{booking_id} updated to {new_status}',
                        'data'   : {'id': booking.id, 'status': booking.status}
                    })
                except Booking.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Booking #{booking_id} not found'})

            # ── CREATE NEW BOOKING ──
            else:

                travel_date = body.get('travel_date', body.get('date', None))

                # Check that travel date is provided
                if not travel_date:
                    return JsonResponse({
                        'success': False,
                        'error': 'Travel date is required.'
                    }, status=400)

                # Check that travel date is not in the past
                try:
                    from datetime import datetime

                    selected_date = datetime.strptime(
                        travel_date, '%Y-%m-%d'
                    ).date()

                    today = timezone.localdate()

                    if selected_date < today:
                        return JsonResponse({
                            'success': False,
                            'error': 'Travel date cannot be in the past.'
                        }, status=400)

                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid travel date format. Use YYYY-MM-DD.'
                    }, status=400)

                # Create booking only after date validation
                booking = Booking.objects.create(
                    full_name=body.get('full_name', body.get('name', '')),
                    email=body.get('email', ''),
                    phone=body.get('phone', ''),
                    destination=body.get('destination', ''),
                    travel_date=selected_date,
                    people=int(body.get('people', body.get('travelers', 1))),
                    budget_inr=float(body.get('budget_inr', body.get('budget', 0))),
                    special_requests=body.get('special_requests', body.get('notes', '')),
                    status='confirmed',
                )

                return JsonResponse({
                    'success': True,
                    'message': 'Booking created successfully',
                    'data': {
                        'booking_id': booking.id,
                        'id': booking.id,
                        'full_name': booking.full_name,
                        'destination': booking.destination,
                        'travel_date': str(booking.travel_date),
                        'status': booking.status
                    }
                })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Method not allowed'})
@csrf_exempt
def reviews(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            Review.objects.create(
                name        = body.get('name',''),
                email       = body.get('email',''),
                destination = body.get('destination',''),
                rating      = int(body.get('rating', 5)),
                review_text = body.get('review_text',''))
            return ok({'message': 'Review submitted! Awaiting approval.'}, 201)
        except Exception as e:
            return err(str(e), 500)
    qs = Review.objects.filter(approved=True)
    return ok([{
        'id': r.id,
        'name': r.name,
        'destination': r.destination,
        'rating': r.rating,
        'review_text': r.review_text,
        'created_at': str(r.created_at)
    } for r in qs])

@csrf_exempt
def ai_recommend(request):
    if request.method != 'POST':
        return err('POST required', 405)
    try:
        body     = json.loads(request.body)
        budget   = float(body.get('budget_inr', 0))
        interest = body.get('interest', 'all').lower()
        duration = int(body.get('duration_days', 5))
        scored   = []
        for d in Destination.objects.filter(is_active=True):
            score = 0
            price = float(d.price_inr)
            if interest != 'all' and d.category == interest:
                score += 50
            elif interest == 'all':
                score += 20
            if price <= budget:
                score += 30
            elif price <= budget * 1.2:
                score += 10
            if abs(d.duration_days - duration) == 0:
                score += 20
            elif abs(d.duration_days - duration) <= 2:
                score += 10
            if budget < 15000 and d.country == 'India':
                score += 25
            if score > 0:
                scored.append((score, d))
        scored.sort(key=lambda x: x[0], reverse=True)
        return ok({
            'recommendations': [{
                'id': d.id,
                'destination_name': d.destination_name,
                'country': d.country,
                'category': d.category,
                'price_inr': float(d.price_inr),
                'price_usd': float(d.price_usd),
                'best_time': d.best_time,
                'duration_days': d.duration_days,
                'image_url': d.image_url,
                'match_score': score,
                'reason': f'Great {d.category} destination within your budget!'
            } for score, d in scored[:3]],
            'message': f'Top {len(scored[:3])} destinations matched!'
        })
    except Exception as e:
        return err(str(e), 500)