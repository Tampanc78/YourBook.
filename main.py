import streamlit as st
import pandas as pd
import plotly.express as px

# Fungsi untuk menyimpan data pengguna ke dalam file CSV
def save_data_to_csv(data, username):
    data.to_csv(f'{username}_data.csv', index=False)

# Fungsi untuk membaca data pengguna dari file CSV
@st.cache(allow_output_mutation=True)
def read_data_from_csv(username):
    try:
        return pd.read_csv(f'{username}_data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Username', 'Pemasukan', 'Persentase_Tabungan', 'Tanggal_Pengeluaran', 'Jumlah_Pengeluaran', 'Jenis_Pengeluaran'])

# Fungsi untuk menyimpan data pengguna
def save_data(username, pemasukan, persentase_tabungan, tanggal_pengeluaran, jumlah_pengeluaran, jenis_pengeluaran):
    data = pd.DataFrame({
        'Username': [username],
        'Pemasukan': [pemasukan],
        'Persentase_Tabungan': [persentase_tabungan],
        'Tanggal_Pengeluaran': [tanggal_pengeluaran],
        'Jumlah_Pengeluaran': [jumlah_pengeluaran],
        'Jenis_Pengeluaran': [jenis_pengeluaran]
    })

    if username in st.session_state.user_data:
        st.session_state.user_data[username] = pd.concat([st.session_state.user_data[username], data], ignore_index=True)
    else:
        st.session_state.user_data[username] = data

    return data

# Fungsi untuk menampilkan halaman login
def show_login_page():
    username = st.text_input("Masukkan Nama Anda:")
    if st.button("Masuk"):
        if 'user_data' in st.session_state and username in st.session_state.user_data:
            st.success(f"Selamat datang kembali, {username}!")
        else:
            st.success(f"Selamat datang, {username}!")
        return True, username
    return False, None

# Fungsi untuk menampilkan halaman tabungan
def show_tabungan_page():
    st.header("Tabungan")
    pemasukan = st.number_input("Pendapatan Bulanan (Rp):", min_value=0)
    
    # Pilihan persentase tabungan
    persentase_options = [15, 20, 25, "Lainnya"]
    persentase_tabungan = st.selectbox("Persentase Tabungan:", persentase_options)

    if persentase_tabungan == "Lainnya":
        persentase_tabungan = st.number_input("Masukkan Persentase Tabungan (0-100):", min_value=0, max_value=100)

    tabungan_amount = (persentase_tabungan / 100) * pemasukan
    sisa_uang = pemasukan - tabungan_amount
    
    st.success(f"Tabungan Anda: Rp {tabungan_amount}")
    st.success(f"Sisa Uang Anda: Rp {sisa_uang}")

    if st.button("Simpan"):
        st.session_state.pemasukan = pemasukan
        st.session_state.persentase_tabungan = persentase_tabungan

        # Tambahkan pesan notifikasi bahwa data tabungan telah berhasil disimpan
        st.success("Data tabungan Anda telah berhasil disimpan!")

# Fungsi untuk menampilkan halaman pengeluaran
def show_pengeluaran_page():
    st.header("Pengeluaran")
    tanggal_pengeluaran = st.date_input("Tanggal Pengeluaran:")
    jumlah_pengeluaran = st.number_input("Jumlah Pengeluaran (Rp):", min_value=0)
    jenis_pengeluaran = st.selectbox("Jenis Pengeluaran:", ["Makan", "Jajan", "Kuliah", "Transportasi", "Lainnya"])

    if st.button("Simpan"):
        data = save_data(
            st.session_state.username,
            st.session_state.pemasukan,
            st.session_state.persentase_tabungan,
            tanggal_pengeluaran,
            jumlah_pengeluaran,
            jenis_pengeluaran
        )
        if 'user_data' in st.session_state:
            if st.session_state.username in st.session_state.user_data:
                st.session_state.user_data[st.session_state.username] = pd.concat([st.session_state.user_data[st.session_state.username], data], ignore_index=True)
            else:
                st.session_state.user_data[st.session_state.username] = data
        else:
            st.session_state.user_data = {st.session_state.username: data}

        # Tambahkan pesan notifikasi bahwa data pengeluaran telah berhasil disimpan
        st.success("Data pengeluaran Anda telah berhasil disimpan!")

# Fungsi untuk menampilkan halaman ringkasan keuangan
def show_ringkasan_page(username):
    if username in st.session_state.user_data:
        data = st.session_state.user_data[username]
        st.write(data)
        category_sum = data.groupby('Jenis_Pengeluaran')['Jumlah_Pengeluaran'].sum().reset_index()
        fig = px.pie(category_sum, values='Jumlah_Pengeluaran', names='Jenis_Pengeluaran', title='Ringkasan Pengeluaran')
        st.plotly_chart(fig)
        pemasukan = data['Pemasukan'].iloc[0]
        persentase_tabungan = data['Persentase_Tabungan'].iloc[0]
        total_pengeluaran = data['Jumlah_Pengeluaran'].sum()
        sisa_uang = pemasukan - total_pengeluaran
        tabungan_amount = (persentase_tabungan / 100) * pemasukan

        if total_pengeluaran > pemasukan:
            st.warning("Uang Anda Habis!")
        elif total_pengeluaran > sisa_uang:
            st.warning("Uang Anda Tidak Cukup!")
        else:
            sisa_setelah_pengeluaran = sisa_uang - total_pengeluaran
            tabungan_amount += sisa_setelah_pengeluaran

            st.success(f"Sisa Uang Anda: Rp {sisa_setelah_pengeluaran}")
            st.success(f"Total Tabungan: Rp {tabungan_amount}")

            if st.button("Finish"):
                st.balloons()
    else:
        st.warning("Data untuk pengguna ini tidak ditemukan.")

# Fungsi untuk menampilkan halaman pengaturan
def show_settings_page(username):
    if username in st.session_state.user_data:
        st.write(f"Data yang telah disimpan untuk pengguna {username}:")
        st.dataframe(st.session_state.user_data[username], height=200)
        selected_rows = st.multiselect("Pilih Baris", st.session_state.user_data[username].index)

        if st.button("Hapus Data Terpilih"):
            selected_data = st.session_state.user_data[username][st.session_state.user_data[username].index.isin(selected_rows)]
            st.write("Data yang akan dihapus:")
            st.write(selected_data)

            st.session_state.user_data[username] = st.session_state.user_data[username][~st.session_state.user_data[username].index.isin(selected_rows)]
            st.success("Data terpilih telah dihapus!")

        if st.button("Hapus Semua Data"):
            st.session_state.user_data[username] = pd.DataFrame(columns=['Username', 'Pemasukan', 'Persentase_Tabungan', 'Tanggal_Pengeluaran', 'Jumlah_Pengeluaran', 'Jenis_Pengeluaran'])
            st.success("Semua data telah dihapus!")
    else:
        st.warning("Data untuk pengguna ini tidak ditemukan.")

# Fungsi utama
def main():
    # Buat session state jika belum ada
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}

    # Tampilkan "YOURBOOK" di sidebar dengan ukuran 4x lebih besar
    st.sidebar.markdown('<h1 style="text-align: center; color: #ffffff;">YOURBOOK</h1>', unsafe_allow_html=True)

    page = st.sidebar.selectbox("Halaman", ["Pengguna", "Tabungan", "Pengeluaran", "Ringkasan", "Pengaturan"])

    if page == "Pengguna":
        logged_in, username = show_login_page()
        if logged_in:
            # Simpan data pengguna
            st.session_state.username = username
            st.sidebar.text(f"Akun: {st.session_state.username}")

    elif page == "Tabungan":
        if hasattr(st.session_state, 'username'):
            show_tabungan_page()

    elif page == "Pengeluaran":
        if hasattr(st.session_state, 'username'):
            show_pengeluaran_page()

    elif page == "Ringkasan":
        if hasattr(st.session_state, 'username') and st.session_state.username in st.session_state.user_data:
            show_ringkasan_page(st.session_state.username)

    elif page == "Pengaturan":
        if hasattr(st.session_state, 'username') and st.session_state.username in st.session_state.user_data:
            show_settings_page(st.session_state.username)

    # Simpan data ke dalam file CSV setiap kali aplikasi dijalankan
    for username, data in st.session_state.user_data.items():
        save_data_to_csv(data, username)

if __name__ == "__main__":
    main()
