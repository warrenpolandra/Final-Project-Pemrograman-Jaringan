# Protokol Chat
v.1.0 03:32 13/06/2023

## FILE SERVER
TUJUAN: Melayani request dari client

## ATURAN PROTOKOL:
- Client mengirimkan request dalam bentuk string
- string harus dalam format: [REQUEST spasi PARAMETER]
- PARAMETER dapat berkembang menjadi PARAMETER1 spasi PARAMETER2 dan seterusnya

## REQUEST YANG DILAYANI:
- informasi umum:
  * Jika request tidak dikenali akan menghasilkan pesan
    - status: ERROR
    - data: request tidak dikenali
  * Semua result akan diberikan dalam bentuk JSON dan diakhiri
    dengan character ascii code #13#10#13#10 atau "\r\n\r\n"

## 1. auth

### TUJUAN
melakukan autentikasi pada user sebelum user bisa mengakses fitur yang ada

### PARAMETER
- PARAMETER1: nama user
- PARAMETER2: password user

### RESULT
* BERHASIL:
  * status: OK
  * data: token user
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 2. logout

### TUJUAN
menyelesaikan session dari user yang sudah melakukan autentikasi

### PARAMETER
tidak ada

### RESULT
* BERHASIL:
  * status: OK
  * data: pesan user sudah logout
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 3. register

### TUJUAN
Mendaftar sebagai user baru di server yang terkoneksi

### PARAMETER
- PARAMETER1: nama user
- PARAMETER2: password user

### RESULT
* BERHASIL:
  * status: OK
  * data: pesan user sudah teregistrasi
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 4. send

### TUJUAN
Mengirim pesan kepada user lain

### PARAMETER
- PARAMETER1: nama user dan id_servernya `[user@id_server]`
- PARAMETER2: pesan

### RESULT
* BERHASIL:
  * status: OK
  * data: informasi bahwa pesan sudah terkirim
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 5. sendgroup

### TUJUAN
Mengirim pesan kepada sebuah grup yang berisi beberapa user

### PARAMETER
- PARAMETER1: id dari group
- PARAMETER2: pesan

### RESULT
* BERHASIL:
  * status: OK
  * data: informasi bahwa pesan sudah terkirim kepada daftar user dalam grup
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 6. sendfile

### TUJUAN
Mengirim file kepada sebuah user

### PARAMETER
- PARAMETER1: nama user dan id servernya `[username@id_server]`
- PARAMETER2: nama file

### RESULT
* BERHASIL:
  * status: OK
  * data: informasi bahwa file sudah terkirim
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 7. inbox

### TUJUAN
Mendapatkan isi dari kotak masuk

### PARAMETER
tidak ada

### RESULT
* BERHASIL:
  * status: OK
  * data: isi dari inbox
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 8. creategroup

### TUJUAN
Membuat grup baru dengan isi user tertentu

### PARAMETER
- PARAMETER1: id grup
- PARAMETER2: daftar user dalam grup dipisahkan dengan `,`. `[user1,user2,user3,...]`

### RESULT
* BERHASIL:
  * status: OK
  * data: pesan grup sudah dibuat
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 9. addserver

### TUJUAN
Menambahkan alamat server tujuan baru

### PARAMETER
- PARAMETER1: id server
- PARAMETER2: ip address dari server tujuan
- PARAMETER3: nomor port dari server tujuan

### RESULT
* BERHASIL:
  * status: OK
  * data: pesan server sudah ditambahkan
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 10. connect

### TUJUAN
Melakukan koneksi pada server yang sudah ditambahkan

### PARAMETER
- PARAMETER1: id server

### RESULT
* BERHASIL:
  * status: OK
  * data: pesan server sudah terkoneksi
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 

## 11. sendfilegroup

### TUJUAN
Mengirim file pada sebuah grup

### PARAMETER
- PARAMETER1: id grup
- PARAMETER2: nama file

### RESULT
* BERHASIL:
  * status: OK
  * data: pesan file sudah terkirim
* GAGAL:
  * status: ERROR
  * data: pesan kesalahan 
