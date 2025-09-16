from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from .models import Santri, Absensi, SuratIzin
from .serializers import SantriSerializer, AbsensiSerializer, SuratIzinSerializer, UserSerializer, RegisterSantriAccountSerializer
from .face_utils import prepare_image_for_face_recognition
from rest_framework import generics, status
from django.utils import timezone
from .face_utils import decode_base64_image, recognize_from_image_pil
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.db import IntegrityError
import datetime
import pandas as pd
import face_recognition
from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.core.cache import cache
import traceback


# REGISTER PENGURUS (AllowAny)
class RegisterPengurusView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
# REGISTER AKUN SANTRI
class RegisterSantriView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSantriAccountSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "id": user.id,
            "username": user.username,
            "role": "santri"
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_get_user(request):
    user = request.user
    role = "pengurus" if user.is_staff else "santri"
    return Response({
        "id": user.id,
        "username": user.username,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "role": role
    })

# SANTRI UPLOAD FOTO WAJAH
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_santri_upload_foto(request):
    if not hasattr(request.user, "santri_profile"):
        return Response({"ok": False, "message": "Bukan akun santri"}, status=403)

    foto = request.FILES.get("foto")
    if not foto:
        return Response({"ok": False, "message": "Upload foto diperlukan"}, status=400)

    santri = request.user.santri_profile
    santri.foto = foto
    santri.save()

    try:
        encs = []

        # 🔥 1. Coba RGB
        try:
            img_np = prepare_image_for_face_recognition(santri.foto.path, force_gray=False)
            print("DEBUG >> coba RGB")
            encs = face_recognition.face_encodings(img_np)
        except Exception as e1:
            print("DEBUG >> gagal di RGB:", str(e1))

        # 🔥 2. Kalau gagal, coba grayscale
        if not encs:
            try:
                img_np = prepare_image_for_face_recognition(santri.foto.path, force_gray=True)
                print("DEBUG >> coba Grayscale")
                encs = face_recognition.face_encodings(img_np)
            except Exception as e2:
                print("DEBUG >> gagal di Grayscale:", str(e2))

        # 🔥 3. Kalau tetep gagal
        if not encs:
            return Response({"ok": False, "message": "Gagal proses wajah: format tidak didukung"}, status=500)

        # Simpan encoding ke DB
        santri.face_encoding = encs[0].tolist()
        santri.save()

        return Response({"ok": True, "message": "Foto berhasil disimpan & wajah terdeteksi"})

    except Exception as e:
        traceback.print_exc()
        return Response({"ok": False, "message": f"Error proses wajah: {str(e)}"}, status=500)



# LOGIN TOKEN-BASED (AllowAny)
class LoginPengurusView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            # cek apakah user ini punya profil santri
            santri_name = None
            role = "pengurus"
            if hasattr(user, "santri_profile"):
                santri_name = user.santri_profile.nama
                role = "santri"

            return Response({
                "token": token.key,
                "role": role,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nama_lengkap": santri_name  # << ini nambahin nama lengkap kalau santri
                }
            })
        return Response({"error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    try:
        if hasattr(request.user, "auth_token"):
            request.user.auth_token.delete()
    except Exception as e:
        print("Logout error:", e)
    return Response({"ok": True, "message": "Logout berhasil"})

class StartAbsensiView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        tanggal = request.data.get("tanggal")
        sesi = request.data.get("sesi")
        if not tanggal or not sesi:
            return Response({"ok": False, "message": "Lengkapi tanggal & sesi"}, status=400)
        cache.set(ABSENSI_KEY, {"tanggal": tanggal, "sesi": sesi, "time": timezone.now()}, 3600)
        return Response({"ok": True, "message": "Absensi dimulai"})
    
class StartTelatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        telat_time = timezone.now()
        cache.set(TELAT_KEY, telat_time, 3600)
        return Response({"ok": True, "message": "Penghitungan keterlambatan dimulai"})
    
ABSENSI_KEY = "absensi_start_time"
TELAT_KEY = "telat_start_time"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_start_absensi(request):
    tanggal = request.data.get("tanggal")
    sesi = request.data.get("sesi")
    if not tanggal or not sesi:
        return Response({"ok": False, "message": "Lengkapi tanggal & sesi"})
    cache.set(ABSENSI_KEY, {"tanggal": tanggal, "sesi": sesi, "time": timezone.now()}, 3600)
    return Response({"ok": True, "message": "Absensi dimulai"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_start_telat(request):
    telat_time = timezone.now()
    cache.set(TELAT_KEY, telat_time, 3600)
    return Response({"ok": True, "message": "Penghitungan keterlambatan dimulai"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_end_absensi(request):
    cache.delete(ABSENSI_KEY)
    cache.delete(TELAT_KEY)
    return Response({"ok": True, "message": "Absensi selesai"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_recognize_and_attend(request):
    data_url = request.data.get('image')
    absensi_info = cache.get(ABSENSI_KEY)
    telat_time = cache.get(TELAT_KEY)

    if not absensi_info:
        return Response({"ok": False, "message": "Absensi belum dimulai"}, status=400)

    tanggal = absensi_info['tanggal']
    sesi = absensi_info['sesi']

    pil_img = decode_base64_image(data_url)
    santri, info = recognize_from_image_pil(pil_img, tolerance=0.5)
    if not santri:
        return Response({"ok": False, "message": "Wajah tidak cocok"}, status=404)

    status_absensi = "Hadir"
    if telat_time:
        diff = (timezone.now() - telat_time).total_seconds() / 60
        if diff <= 5: status_absensi = "T1"
        elif diff <= 15: status_absensi = "T2"
        else: status_absensi = "T3"

    Absensi.objects.update_or_create(
        santri=santri,
        tanggal=tanggal,
        sesi=sesi,
        defaults={"status": status_absensi, "created_by": request.user}
    )
    return Response({"ok": True, "santri": santri.nama, "status": status_absensi})

# LIST SANTRI
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_list_santri(request):
    santris = Santri.objects.all().order_by('santri_id')
    return Response({'ok': True, 'data': SantriSerializer(santris, many=True).data})

# UPLOAD SURAT IZIN (santri or pengurus) — santri can upload, auto approved
@api_view(['POST'])
@permission_classes([AllowAny])  # allow any so unauthenticated santri can upload; but ideally use token per santri later
def api_upload_surat_izin(request):
    # expected: santri_pk, tanggal (YYYY-MM-DD), sesi, file
    santri_pk = request.data.get('santri_pk')
    tanggal = request.data.get('tanggal')
    sesi = request.data.get('sesi')
    file = request.FILES.get('file')
    if not (santri_pk and tanggal and sesi and file):
        return Response({'ok': False, 'message': 'Lengkapi data'}, status=400)
    try:
        s = Santri.objects.get(pk=santri_pk)
    except Santri.DoesNotExist:
        return Response({'ok': False, 'message': 'Santri tidak ditemukan'}, status=404)
    try:
        si = SuratIzin(santri=s, tanggal=tanggal, sesi=sesi, file=file, uploaded_by=request.user if request.user.is_authenticated else None, status='Disetujui')
        si.save()
    except IntegrityError:
        return Response({'ok': False, 'message': 'Sudah ada surat izin untuk santri ini pada tanggal & sesi tersebut'}, status=400)
    return Response({'ok': True, 'surat': SuratIzinSerializer(si).data})

# RECOGNIZE & ATTEND (pengurus only) — expects image (base64), tanggal, sesi
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_recognize_and_attend(request):
    data_url = request.data.get('image')
    tanggal = request.data.get('tanggal')
    sesi = request.data.get('sesi')
    if not (data_url and tanggal and sesi):
        return Response({'ok': False, 'message': 'Lengkapi data (image, tanggal, sesi)'}, status=400)
    try:
        pil_img = decode_base64_image(data_url)
    except Exception:
        return Response({'ok': False, 'message': 'Image decode gagal'}, status=400)
    santri, info = recognize_from_image_pil(pil_img, tolerance=0.5)
    if santri is None:
        if info == "no_face":
            return Response({'ok': False, 'message': 'Wajah tidak terdeteksi'}, status=400)
        elif info == "no_dataset":
            return Response({'ok': False, 'message': 'Data wajah kosong'}, status=400)
        else:
            return Response({'ok': False, 'message': 'Wajah tidak cocok'}, status=404)
    # tentukan status based on waktu sekarang vs jadwal sesi
    # definisi jam mulai berdasarkan sesi (sesuaikan jika diperlukan)
    sesi_jam_mulai = {'Subuh': (4,0), 'Sore': (15,0), 'Malam': (19,0)}
    now = timezone.localtime(timezone.now())
    try:
        t_year, t_month, t_day = [int(x) for x in tanggal.split('-')]
        jadwal_hour, jadwal_minute = sesi_jam_mulai.get(sesi, (8,0))
        t_mulai = timezone.make_aware(datetime.datetime(t_year, t_month, t_day, jadwal_hour, jadwal_minute))
    except Exception:
        # fallback gunakan now
        t_mulai = timezone.make_aware(datetime.datetime(now.year, now.month, now.day, 8, 0))

    diff = now - t_mulai
    minutes_late = diff.total_seconds() / 60
    if minutes_late <= 0:
        status_str = 'Hadir'
    elif minutes_late <= 5:
        status_str = 'T1'
    elif minutes_late <= 15:
        status_str = 'T2'
    else:
        status_str = 'T3'

    # simpan absensi (unique per santri,tanggal,sesi)
    try:
        a, created = Absensi.objects.update_or_create(
            santri=santri,
            tanggal=tanggal,
            sesi=sesi,
            defaults={'status': status_str, 'created_by': request.user, 'waktu_scan': now}
        )
    except Exception as e:
        return Response({'ok': False, 'message': f'Gagal simpan absensi: {str(e)}'}, status=500)

    return Response({'ok': True, 'santri': {'id': santri.id, 'santri_id': santri.santri_id, 'nama': santri.nama}, 'status': status_str})

# REKAP pivot (range) — returns JSON pivot and also we have export endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_rekap(request):
    # params: start (YYYY-MM-DD), end (YYYY-MM-DD)
    start = request.GET.get('start')
    end = request.GET.get('end')
    if not start or not end:
        return Response({'ok': False, 'message': 'start & end required'}, status=400)
    try:
        start_dt = datetime.datetime.fromisoformat(start).date()
        end_dt = datetime.datetime.fromisoformat(end).date()
    except:
        return Response({'ok': False, 'message': 'Format date salah'}, status=400)
    # buat list tanggal+sesi (urut)
    all_dates = []
    d = start_dt
    while d <= end_dt:
        all_dates.append(d)
        d += datetime.timedelta(days=1)
    sesi_list = ['Subuh','Sore','Malam']
    headers = []
    for dt in all_dates:
        for ss in sesi_list:
            headers.append({'tanggal': dt.isoformat(), 'sesi': ss, 'col_key': f"{dt.isoformat()}_{ss}"})

    # group santri by gender
    santri_putra = Santri.objects.filter(jenis_kelamin='L').order_by('nama')
    santri_putri = Santri.objects.filter(jenis_kelamin='P').order_by('nama')

    def build_table(santri_queryset):
        rows = []
        for s in santri_queryset:
            row = {'santri_id': s.santri_id, 'nama': s.nama}
            for h in headers:
                # cek Absensi
                a = Absensi.objects.filter(santri=s, tanggal=h['tanggal'], sesi=h['sesi']).first()
                if a:
                    row[h['col_key']] = a.status
                else:
                    # cek izin
                    izin = SuratIzin.objects.filter(santri=s, tanggal=h['tanggal'], sesi=h['sesi'], status='Disetujui').first()
                    if izin:
                        row[h['col_key']] = 'Izin'
                    else:
                        row[h['col_key']] = 'Alfa'
            rows.append(row)
        return rows

    putra_rows = build_table(santri_putra)
    putri_rows = build_table(santri_putri)

    return Response({'ok': True, 'headers': headers, 'putra': putra_rows, 'putri': putri_rows})

# EXPORT XLSX (sheet putra & putri)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_export_xlsx(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    if not start or not end:
        return Response({'ok': False, 'message': 'start & end required'}, status=400)
    # reuse api_rekap logic
    resp = api_rekap(request)
    if resp.status_code != 200:
        return resp
    data = resp.data
    headers = data['headers']
    putra = data['putra']
    putri = data['putri']

    # build DataFrame for each
    cols = ['santri_id','nama'] + [h['col_key'] for h in headers]
    df_putra = pd.DataFrame([{**{k:v for k,v in r.items() if k in ['santri_id','nama']}, **{h['col_key']: r[h['col_key']] for h in headers}} for r in putra])
    df_putri = pd.DataFrame([{**{k:v for k,v in r.items() if k in ['santri_id','nama']}, **{h['col_key']: r[h['col_key']] for h in headers}} for r in putri])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_putra.to_excel(writer, index=False, sheet_name='Putra')
        df_putri.to_excel(writer, index=False, sheet_name='Putri')
    output.seek(0)
    response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=rekap_absensi.xlsx'
    return response

# EXPORT PDF (simple) - combines putra & putri pages
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_export_pdf(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    resp = api_rekap(request)
    if resp.status_code != 200:
        return resp
    data = resp.data
    headers = data['headers']
    putra = data['putra']
    putri = data['putri']

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 10)
    y = 800
    def draw_section(title, rows):
        nonlocal p, y
        p.drawString(50, y, title); y -= 20
        # header
        header_line = "Nama".ljust(30) + " | " + " | ".join([h['col_key'] for h in headers])
        p.drawString(50, y, header_line); y -= 15
        for r in rows:
            line = f"{r['nama']}".ljust(30) + " | " + " | ".join([str(r[h['col_key']]) for h in headers])
            if y < 50:
                p.showPage(); y = 800
            p.drawString(50, y, line); y -= 12
        y -= 20

    draw_section("Putra", putra)
    draw_section("Putri", putri)
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
