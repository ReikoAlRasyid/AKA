import random
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

# ========== 1. GENERATOR DATA UJI ==========
def generate_luhn_valid_card(length=16):
    """Generate nomor kartu yang valid menurut Luhn Algorithm"""
    digits = [random.randint(0, 9) for _ in range(length - 1)]
    total = 0
    is_even = False
    
    for i in range(length - 2, -1, -1):
        digit = digits[i]
        if is_even:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
        is_even = not is_even
    
    check_digit = (10 - (total % 10)) % 10
    digits.append(check_digit)
    return ''.join(map(str, digits))

def generate_test_data(batch_sizes):
    """Generate data uji untuk semua batch size"""
    all_data = {}
    
    for size in batch_sizes:
        data_batch = []
        for _ in range(size):
            length = random.choice([13, 16, 19])
            # Generate valid card
            valid_card = generate_luhn_valid_card(length)
            data_batch.append(valid_card)
            
            # Generate invalid version (50% of batch)
            if len(data_batch) < size:
                card_list = list(valid_card)
                card_list[-1] = str((int(card_list[-1]) + 1) % 10)
                invalid_card = ''.join(card_list)
                data_batch.append(invalid_card)
        
        random.shuffle(data_batch)
        all_data[size] = data_batch
    
    return all_data

# ========== 2. ALGORITMA LUHN ==========
def luhn_iterative(card_number):
    """Versi iteratif"""
    card_str = str(card_number).replace(" ", "")
    total = 0
    is_even = False
    
    for digit_char in reversed(card_str):
        digit = int(digit_char)
        if is_even:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
        is_even = not is_even
    
    return total % 10 == 0

def luhn_recursive(card_number, index=0, total=0, is_even=False):
    """Versi rekursif"""
    card_str = str(card_number).replace(" ", "")
    
    if index >= len(card_str):
        return total % 10 == 0
    
    digit_index = len(card_str) - index - 1
    digit = int(card_str[digit_index])
    
    if is_even:
        digit *= 2
        if digit > 9:
            digit -= 9
    
    return luhn_recursive(card_str, index + 1, total + digit, not is_even)

# ========== 3. FUNGSI PENGUJIAN ==========
def run_performance_tests(batch_sizes=[1, 5, 10, 100, 500]):
    """Jalankan pengujian untuk semua batch size"""
    results = {
        'batch_sizes': batch_sizes,
        'iterative_times': [],
        'recursive_times': [],
        'speedup_factors': [],
        'iterative_per_card': [],
        'recursive_per_card': []
    }
    
    # Generate semua data sekaligus
    print("Mengenerate data uji...")
    test_data = generate_test_data(batch_sizes)
    
    for size in batch_sizes:
        print(f"\n{'='*50}")
        print(f"MENGUJI {size} DATA")
        print(f"{'='*50}")
        
        data_batch = test_data[size]
        
        # Test Iterative
        start_time = time.perf_counter_ns()
        for card in data_batch:
            luhn_iterative(card)
        end_time = time.perf_counter_ns()
        iterative_time_ns = end_time - start_time
        iterative_time_ms = iterative_time_ns / 1e6
        
        # Test Recursive
        start_time = time.perf_counter_ns()
        for card in data_batch:
            luhn_recursive(card)
        end_time = time.perf_counter_ns()
        recursive_time_ns = end_time - start_time
        recursive_time_ms = recursive_time_ns / 1e6
        
        # Calculate metrics
        speedup = recursive_time_ms / iterative_time_ms if iterative_time_ms > 0 else 0
        avg_iterative_ns = iterative_time_ns / size
        avg_recursive_ns = recursive_time_ns / size
        
        # Store results
        results['iterative_times'].append(iterative_time_ms)
        results['recursive_times'].append(recursive_time_ms)
        results['speedup_factors'].append(speedup)
        results['iterative_per_card'].append(avg_iterative_ns)
        results['recursive_per_card'].append(avg_recursive_ns)
        
        # Print summary
        print(f"Waktu Total:")
        print(f"  Iteratif: {iterative_time_ms:.4f} ms")
        print(f"  Rekursif: {recursive_time_ms:.4f} ms")
        print(f"\nPer Kartu:")
        print(f"  Iteratif: {avg_iterative_ns:.2f} ns")
        print(f"  Rekursif: {avg_recursive_ns:.2f} ns")
        print(f"\nSpeedup Factor: {speedup:.2f}x")
        
        # Show sample data for small batches
        if size <= 10:
            print(f"\nContoh {min(3, size)} kartu:")
            for i in range(min(3, size)):
                card = data_batch[i]
                valid = luhn_iterative(card)
                print(f"  {card[:4]}...{card[-4:]} ({len(card)} digit) → {'VALID' if valid else 'INVALID'}")
    
    return results, test_data

# ========== 4. VISUALISASI GRAFIK LENGKAP ==========
def create_comprehensive_visualization(results):
    """Buat 4 grafik dalam satu figure"""
    # Setup figure dengan GridSpec untuk layout yang lebih fleksibel
    fig = plt.figure(figsize=(18, 12))
    gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # Data
    sizes = results['batch_sizes']
    iterative_times = results['iterative_times']
    recursive_times = results['recursive_times']
    speedups = results['speedup_factors']
    iterative_per_card = results['iterative_per_card']
    recursive_per_card = results['recursive_per_card']
    
    # ---------- GRAFIK 1: Total Waktu vs Jumlah Data ----------
    ax1 = fig.add_subplot(gs[0, 0])
    
    # Plot dengan area fill
    ax1.fill_between(sizes, iterative_times, alpha=0.3, color='blue', label='Iteratif')
    ax1.fill_between(sizes, recursive_times, alpha=0.3, color='red', label='Rekursif')
    
    # Plot garis
    ax1.plot(sizes, iterative_times, 'b-o', linewidth=2, markersize=8, label='Iteratif')
    ax1.plot(sizes, recursive_times, 'r-s', linewidth=2, markersize=8, label='Rekursif')
    
    ax1.set_xlabel('Jumlah Data', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Waktu Total (ms)', fontsize=11, fontweight='bold')
    ax1.set_title('TOTAL WAKTU EKSEKUSI', fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper left')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Anotasi trend
    ax1.text(0.05, 0.95, 'Linear O(n)', transform=ax1.transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
    
    # ---------- GRAFIK 2: Speedup Factor ----------
    ax2 = fig.add_subplot(gs[0, 1])
    
    # Bar chart dengan gradient warna
    colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.7, len(speedups)))
    bars = ax2.bar(range(len(sizes)), speedups, color=colors, edgecolor='black', linewidth=1.5)
    
    # Anotasi nilai di atas bar
    for i, (bar, speedup) in enumerate(zip(bars, speedups)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{speedup:.1f}x', ha='center', va='bottom', fontweight='bold')
    
    ax2.set_xlabel('Jumlah Data', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Speedup Factor', fontsize=11, fontweight='bold')
    ax2.set_title('ITERATIF BERAPA KALI LEBIH CEPAT', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xticks(range(len(sizes)))
    ax2.set_xticklabels(sizes)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax2.axhline(y=1.0, color='black', linestyle='--', alpha=0.5)
    
    # ---------- GRAFIK 3: Waktu per Kartu ----------
    ax3 = fig.add_subplot(gs[0, 2])
    
    # Scatter plot dengan ukuran marker berdasarkan batch size
    sizes_for_scatter = [s/50 for s in sizes]  # Scale untuk ukuran marker
    
    sc1 = ax3.scatter(sizes, iterative_per_card, s=sizes_for_scatter, 
                      c='blue', alpha=0.7, edgecolors='black', linewidth=1, label='Iteratif')
    sc2 = ax3.scatter(sizes, recursive_per_card, s=sizes_for_scatter, 
                      c='red', alpha=0.7, edgecolors='black', linewidth=1, label='Rekursif')
    
    # Garis trend
    z_iter = np.polyfit(sizes, iterative_per_card, 1)
    p_iter = np.poly1d(z_iter)
    z_recur = np.polyfit(sizes, recursive_per_card, 1)
    p_recur = np.poly1d(z_recur)
    
    ax3.plot(sizes, p_iter(sizes), 'b--', alpha=0.5, linewidth=1)
    ax3.plot(sizes, p_recur(sizes), 'r--', alpha=0.5, linewidth=1)
    
    ax3.set_xlabel('Jumlah Data', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Waktu per Kartu (ns)', fontsize=11, fontweight='bold')
    ax3.set_title('EFISIENSI PER UNIT DATA', fontsize=13, fontweight='bold', pad=15)
    ax3.grid(True, alpha=0.3, linestyle='--')
    ax3.legend()
    
    # Anotasi rata-rata
    avg_iter = np.mean(iterative_per_card)
    avg_recur = np.mean(recursive_per_card)
    ax3.axhline(y=avg_iter, color='blue', linestyle=':', alpha=0.5)
    ax3.axhline(y=avg_recur, color='red', linestyle=':', alpha=0.5)
    ax3.text(max(sizes)*0.7, avg_iter*1.1, f'Rata: {avg_iter:.0f} ns', 
             color='blue', fontsize=9, fontweight='bold')
    ax3.text(max(sizes)*0.7, avg_recur*0.9, f'Rata: {avg_recur:.0f} ns', 
             color='red', fontsize=9, fontweight='bold')
    
    # ---------- GRAFIK 4: Perbandingan Stacked Bar ----------
    ax4 = fig.add_subplot(gs[1, :])
    
    # Data untuk stacked bar
    x = range(len(sizes))
    width = 0.35
    
    bars1 = ax4.bar(x, iterative_times, width, label='Iteratif', color='blue', alpha=0.8)
    bars2 = ax4.bar(x, [r-i for r,i in zip(recursive_times, iterative_times)], width, 
                    bottom=iterative_times, label='Overhead Rekursi', color='red', alpha=0.5)
    
    # Anotasi persentase
    for i, (it, rt) in enumerate(zip(iterative_times, recursive_times)):
        percentage = (it / rt) * 100
        ax4.text(i, it/2, f'{percentage:.0f}%', ha='center', va='center', 
                fontweight='bold', color='white', fontsize=10)
        ax4.text(i, it + (rt-it)/2, f'Overhead\n{100-percentage:.0f}%', 
                ha='center', va='center', fontweight='bold', color='white', fontsize=9)
    
    ax4.set_xlabel('Jumlah Data', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Waktu (ms)', fontsize=11, fontweight='bold')
    ax4.set_title('KOMPOSISI WAKTU: ITERATIF vs OVERHEAD REKURSI', fontsize=13, fontweight='bold', pad=15)
    ax4.set_xticks(x)
    ax4.set_xticklabels([f'{s}\ndata' for s in sizes])
    ax4.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax4.legend(loc='upper left')
    
    # ---------- GRAFIK 5: Perbandingan Ratio (Mini) ----------
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.axis('off')
    
    # Buat tabel perbandingan
    table_data = []
    headers = ['Data', 'Iteratif', 'Rekursif', 'Ratio']
    
    for i, size in enumerate(sizes):
        table_data.append([
            f'{size}',
            f'{iterative_times[i]:.3f} ms',
            f'{recursive_times[i]:.3f} ms',
            f'{speedups[i]:.2f}x'
        ])
    
    table = ax5.table(cellText=table_data, colLabels=headers,
                     cellLoc='center', loc='center',
                     colColours=['#f0f0f0']*4)
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    
    # Judul untuk tabel
    ax5.set_title('RINGKASAN PERFORMA', fontsize=12, fontweight='bold', pad=20)
    
    # ---------- JUDUL UTAMA ----------
    plt.suptitle('ANALISIS KOMPREHENSIF ALGORITMA LUHN: ITERATIF vs REKURSIF\n'
                'Pengujian dengan Variasi Jumlah Data', 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Simpan grafik
    plt.savefig('luhn_performance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

# ========== 5. GRAFIK TAMBAHAN: ANALISIS DETIL ==========
def create_detailed_analysis_graph(results, test_data):
    """Buat grafik analisis detil"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    sizes = results['batch_sizes']
    
    # 1. Distribusi Waktu per Batch
    ax1 = axes[0, 0]
    x_pos = np.arange(len(sizes))
    ax1.bar(x_pos - 0.2, results['iterative_times'], 0.4, label='Iteratif', color='blue', alpha=0.7)
    ax1.bar(x_pos + 0.2, results['recursive_times'], 0.4, label='Rekursif', color='red', alpha=0.7)
    
    ax1.set_xlabel('Jumlah Data', fontsize=11)
    ax1.set_ylabel('Waktu (ms)', fontsize=11)
    ax1.set_title('DISTRIBUSI WAKTU PER BATCH', fontsize=13, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(sizes)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Efisiensi Memory (Estimasi)
    ax2 = axes[0, 1]
    # Estimasi: iteratif O(1) memory, rekursif O(n) memory
    memory_iterative = [1] * len(sizes)  # Konstan
    memory_recursive = [size/10 for size in sizes]  # Linear
    
    ax2.plot(sizes, memory_iterative, 'b-o', label='Iteratif (O(1))', linewidth=2)
    ax2.plot(sizes, memory_recursive, 'r-s', label='Rekursif (O(n))', linewidth=2)
    
    ax2.set_xlabel('Jumlah Data', fontsize=11)
    ax2.set_ylabel('Estimasi Memory Usage', fontsize=11)
    ax2.set_title('KOMPLEKSITAS MEMORI', fontsize=13, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Perbandingan Linear vs Log Scale
    ax3 = axes[1, 0]
    ax3.plot(sizes, results['iterative_per_card'], 'b-o', label='Iteratif/Data', linewidth=2)
    ax3.plot(sizes, results['recursive_per_card'], 'r-s', label='Rekursif/Data', linewidth=2)
    
    ax3.set_xlabel('Jumlah Data', fontsize=11)
    ax3.set_ylabel('Waktu per Data (ns)', fontsize=11)
    ax3.set_title('WAKTU PER UNIT DATA', fontsize=13, fontweight='bold')
    ax3.set_xscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Heatmap Speedup
    ax4 = axes[1, 1]
    speedup_matrix = np.array(results['speedup_factors']).reshape(1, -1)
    im = ax4.imshow(speedup_matrix, cmap='RdYlGn_r', aspect='auto')
    
    ax4.set_xticks(range(len(sizes)))
    ax4.set_xticklabels(sizes)
    ax4.set_yticks([])
    ax4.set_title('HEATMAP SPEEDUP FACTOR', fontsize=13, fontweight='bold')
    
    # Anotasi nilai di heatmap
    for i, speedup in enumerate(results['speedup_factors']):
        color = 'white' if speedup > 2 else 'black'
        ax4.text(i, 0, f'{speedup:.2f}x', ha='center', va='center', 
                color=color, fontweight='bold', fontsize=11)
    
    plt.colorbar(im, ax=ax4, orientation='horizontal', pad=0.2)
    
    plt.suptitle('ANALISIS DETIL: ITERATIF vs REKURSIF\n', 
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

# ========== 6. FUNGSI UTAMA ==========
def main():
    """Program utama"""
    print("="*70)
    print("VISUALISASI ANALISIS PERFORMA ALGORITMA LUHN")
    print("="*70)
    
    # Tentukan batch sizes
    batch_sizes = [1, 5, 10, 100, 500]
    
    # Jalankan pengujian
    print("\n🚀 MEMULAI PENGUJIAN...")
    results, test_data = run_performance_tests(batch_sizes)
    
    # Buat visualisasi utama
    print("\n📊 MEMBUAT VISUALISASI UTAMA...")
    fig1 = create_comprehensive_visualization(results)
    
    # Buat visualisasi tambahan
    print("📈 MEMBUAT ANALISIS DETIL...")
    create_detailed_analysis_graph(results, test_data)
    
    # Tampilkan kesimpulan
    print("\n" + "="*70)
    print("KESIMPULAN ANALISIS")
    print("="*70)
    
    avg_speedup = np.mean(results['speedup_factors'])
    max_speedup = max(results['speedup_factors'])
    min_speedup = min(results['speedup_factors'])
    
    print(f"\n📌 HASIL UTAMA:")
    print(f"   • Rata-rata speedup: {avg_speedup:.2f}x")
    print(f"   • Speedup terbaik: {max_speedup:.2f}x")
    print(f"   • Speedup terburuk: {min_speedup:.2f}x")
    
    print(f"\n📌 REKOMENDASI:")
    if avg_speedup > 1.5:
        print(f"   ✅ GUNAKAN ITERATIF: {avg_speedup:.1f}x lebih cepat")
    else:
        print(f"   ⚠️  Boleh pilih salah satu: Perbedaan tidak signifikan")
    
    print(f"\n📌 DETAIL PER BATCH:")
    for i, size in enumerate(batch_sizes):
        print(f"   • {size:4d} data: Iteratif {results['speedup_factors'][i]:.2f}x lebih cepat")
    
    print("\n💾 Grafik telah disimpan sebagai 'luhn_performance_analysis.png'")
    
    # Tampilkan contoh data
    print("\n" + "="*70)
    print("CONTOH DATA UJI (Batch 5 data):")
    print("="*70)
    
    sample_batch = test_data[5][:3]  # Ambil 3 contoh
    for i, card in enumerate(sample_batch):
        valid_iter = luhn_iterative(card)
        valid_recur = luhn_recursive(card)
        print(f"\nKartu {i+1}: {card}")
        print(f"   Panjang : {len(card)} digit")
        print(f"   Iteratif: {'VALID' if valid_iter else 'INVALID'}")
        print(f"   Rekursif: {'VALID' if valid_recur else 'INVALID'}")
        print(f"   Konsisten: {valid_iter == valid_recur}")

if __name__ == "__main__":
    main()