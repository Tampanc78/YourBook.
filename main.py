import streamlit as st
import pandas as pd
import plotly.express as px

def save_data_to_csv(data):
    data.to_csv('user_data.csv', index=False)

def read_data_from_csv():
    try:
        return pd.read_csv('user_data.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Username', 'Pemasukan', 'Persentase_Tabungan', 'Tanggal_Pengeluaran', 'Jumlah_Pengeluaran', 'Jenis_Pengeluaran'])

def save_data(username, pemasukan, persentase_tabungan, tanggal_pengeluaran, jumlah_pengeluaran, jenis_pengeluaran):
    data = pd.DataFrame({
        'Username': [username],
        'Pemasukan': [pemasukan],
        'Persentase_Tabungan': [persentase_tabungan],
        'Tanggal_Pengeluaran': [tanggal_pengeluaran],
        'Jumlah_Pengeluaran': [jumlah_pengeluaran],
        'Jenis_Pengeluaran': [jenis_pengeluaran]
    })
    return data

def show_login_page():
    username = st.text_input("Masukkan Nama Anda:")
    if st.button("Masuk"):
        if 'data' in st.session_state and not st.session_state.data.empty:
            if username in st.session_state.data['Username'].values:
                st.success(f"Selamat datang kembali, {username}!")
            else:
                st.success(f"Selamat datang, {username}!")
        else:
            st.success(f"Selamat datang, {username}!")
        return True, username
    return False, None

def show_tabungan_page():
    st.header("Tabungan")
    pemasukan = st.number_input("Pendapatan Bulanan (Rp):", min_value=0)

    persentase_tabungan = st.selectbox("Persentase Tabungan:", [15, 20, 25])
    tabungan_amount = (persentase_tabungan / 100) * pemasukan
    sisa_uang = pemasukan - tabungan_amount
    
    st.success(f"Tabungan Anda: Rp {tabungan_amount}")
    st.success(f"Sisa Uang Anda: Rp {sisa_uang}")

    if st.button("Simpan"):
        st.session_state.pemasukan = pemasukan
        st.session_state.persentase_tabungan = persentase_tabungan

        st.success("tabungan tersimpan, jangan boros boros ya!")

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
        if 'data' in st.session_state:
            st.session_state.data = pd.concat([st.session_state.data, data], ignore_index=True)
        else:
            st.session_state.data = data

        st.success("Pengeluaran sudah dicatat, jangan boros ya!")

def show_ringkasan_page(data):
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

def show_settings_page(data):
    st.write("Data yang telah disimpan:")

    st.dataframe(data, height=200)

    selected_rows = st.multiselect("Pilih Baris", data.index)

    if st.button("Hapus Data Terpilih"):
        selected_data = data[data.index.isin(selected_rows)]
        st.write("Data yang akan dihapus:")
        st.write(selected_data)

        data = data[~data.index.isin(selected_rows)]
        st.session_state.data = data
        st.success("Data terpilih telah dihapus!")

    if st.button("Hapus Semua Data"):
        st.session_state.data = pd.DataFrame(columns=['Username', 'Pemasukan', 'Persentase_Tabungan', 'Tanggal_Pengeluaran', 'Jumlah_Pengeluaran', 'Jenis_Pengeluaran'])
        st.success("Semua data telah dihapus!")

def main():
    if 'data' not in st.session_state:
        st.session_state.data = read_data_from_csv()

    st.sidebar.markdown('<h1 style="text-align: center; color: #ffffff;">YOURBOOK</h1>', unsafe_allow_html=True)

    page = st.sidebar.selectbox("Halaman", ["Pengguna", "Tabungan", "Pengeluaran", "Ringkasan", "Pengaturan"])

    if page == "Pengguna":
        logged_in, username = show_login_page()
        if logged_in:
            st.session_state.username = username
            st.sidebar.text(f"Akun: {st.session_state.username}")

    elif page == "Tabungan":
        if hasattr(st.session_state, 'username'):
            show_tabungan_page()

    elif page == "Pengeluaran":
        if hasattr(st.session_state, 'username'):
            show_pengeluaran_page()

    elif page == "Ringkasan":
        if hasattr(st.session_state, 'data'):
            show_ringkasan_page(st.session_state.data)

    elif page == "Pengaturan":
        show_settings_page(st.session_state.data)

    save_data_to_csv(st.session_state.data)

if __name__ == "__main__":
    main()
