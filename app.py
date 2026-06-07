# app.py - Deshidratación de Arándano
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Configuración de la página
st.set_page_config(
    page_title="Deshidratación de Arándano",
    page_icon="🫐",
    layout="wide"
)

# Título
st.title("🫐 Balance de Masa - Deshidratación de Arándano")
st.markdown("---")

# Función de cálculo
def calcular_balance(F, Mc, Hi, Hf, Mp):
    # Cálculos
    Fu = F - Mc  # Fruta útil después de merma de calidad
    solidos = Fu * (1 - Hi/100)  # Sólidos totales
    Ps = solidos / (1 - Hf/100)  # Peso después de secado
    PF = Ps - Mp  # Producto final
    Agua_elim = Fu - Ps  # Agua eliminada
    
    # Verificar errores
    if PF < 0:
        return None
    
    resultados = {
        'PF': PF,
        'Fu': Fu,
        'Ps': Ps,
        'Agua_elim': Agua_elim,
        'solidos': solidos,
        'rendimiento': (PF/F)*100,
        'mermas_totales': Mc + Mp,
        'agua_eliminada': Agua_elim
    }
    return resultados

# Sidebar con controles
with st.sidebar:
    st.header("⚙️ Parámetros del proceso")
    
    st.subheader("📦 Materia Prima")
    F = st.slider(
        "🫐 Arándano fresco (kg)",
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        help="Cantidad de arándano fresco en kilogramos"
    )
    
    st.subheader("❌ Mermas")
    Mc = st.slider(
        "Merma por calidad (kg)",
        min_value=0.0,
        max_value=2.0,
        value=0.1,
        step=0.05,
        help="Arándanos que no pasan control de calidad"
    )
    
    Mp = st.slider(
        "Merma en proceso (kg)",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        step=0.05,
        help="Pérdidas durante el procesamiento"
    )
    
    st.subheader("💧 Humedad")
    Hi = st.slider(
        "Humedad inicial (%)",
        min_value=75.0,
        max_value=90.0,
        value=85.0,
        step=1.0,
        help="Humedad del arándano fresco"
    )
    
    Hf = st.slider(
        "Humedad final (%)",
        min_value=8.0,
        max_value=20.0,
        value=12.0,
        step=1.0,
        help="Humedad deseada después del secado"
    )

# Botón de cálculo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    calcular = st.button("🔍 CALCULAR BALANCE", type="primary", use_container_width=True)

# Resultados
if calcular:
    resultados = calcular_balance(F, Mc, Hi, Hf, Mp)
    
    if resultados:
        # Métricas principales
        st.markdown("## 📊 Resultados del Balance")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🫐 Producto Final", f"{resultados['PF']:.3f} kg", f"{resultados['PF']*1000:.0f} g")
        with col2:
            st.metric("📊 Rendimiento", f"{resultados['rendimiento']:.1f}%")
        with col3:
            st.metric("📉 Mermas Totales", f"{resultados['mermas_totales']:.3f} kg")
        with col4:
            st.metric("💧 Agua Eliminada", f"{resultados['agua_eliminada']:.3f} kg")
        
        # Tabla de proceso
        st.markdown("### 📋 Detalle del Proceso")
        proceso_df = pd.DataFrame({
            'Etapa': [
                'Arándano fresco',
                'Después de control calidad',
                'Después del secado',
                'Producto final'
            ],
            'Masa (kg)': [
                F,
                resultados['Fu'],
                resultados['Ps'],
                resultados['PF']
            ],
            'Pérdida Acumulada (kg)': [
                0,
                Mc,
                Mc + (F - resultados['Ps']),
                Mc + Mp + (F - resultados['Ps'])
            ],
            'Humedad (%)': [
                Hi,
                Hi,
                Hf,
                Hf
            ]
        })
        st.dataframe(proceso_df.style.format({
            'Masa (kg)': '{:.3f}',
            'Pérdida Acumulada (kg)': '{:.3f}',
            'Humedad (%)': '{:.1f}%'
        }), use_container_width=True)
        
        # Gráficos
        st.markdown("### 📈 Visualización del Proceso")
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            etapas = ['Fresco', 'Después\nmerma', 'Después\nsecado', 'Final']
            valores = [F, resultados['Fu'], resultados['Ps'], resultados['PF']]
            colores = ['#4CAF50', '#8BC34A', '#FF9800', '#F44336']
            
            bars = ax1.bar(etapas, valores, color=colores, edgecolor='black')
            for bar, v in zip(bars, valores):
                ax1.text(bar.get_x() + bar.get_width()/2, v + max(valores)*0.02,
                        f'{v:.3f} kg', ha='center', fontweight='bold', fontsize=9)
            
            # Línea de tendencia
            ax1.plot(range(len(etapas)), valores, 'b--o', linewidth=2, markersize=8, alpha=0.5)
            ax1.set_ylabel('Masa (kg)')
            ax1.set_title('Evolución del peso durante el proceso')
            ax1.grid(axis='y', alpha=0.3)
            st.pyplot(fig1)
            plt.close()
        
        with col2:
            # Gráfico de pastel
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            distribucion = {
                'Producto final': resultados['PF'],
                'Agua eliminada': resultados['Agua_elim'],
                'Merma calidad': Mc,
                'Merma proceso': Mp
            }
            colores_pie = ['#4CAF50', '#2196F3', '#9E9E9E', '#FF9800']
            explode = (0.1, 0, 0, 0)
            
            ax2.pie(distribucion.values(), labels=distribucion.keys(),
                   autopct='%1.1f%%', colors=colores_pie, explode=explode)
            ax2.set_title(f'Distribución (Base: {F} kg frescos)')
            st.pyplot(fig2)
            plt.close()
        
        # Información adicional de sólidos
        with st.expander("🔬 Información Técnica"):
            st.info(f"""
            **Detalles del cálculo:**
            - Sólidos totales: {resultados['solidos']:.3f} kg
            - Agua en fresco: {F * Hi/100:.3f} kg
            - Agua en producto final: {resultados['PF'] * Hf/100:.3f} kg
            - Relación de concentración: {F/resultados['PF']:.1f}:1
            """)
        
    else:
        st.error("⚠️ ERROR: Las mermas exceden la masa disponible en alguna etapa!")
        st.warning(f"Revisa los valores ingresados: Merma calidad ({Mc} kg) + Merma proceso ({Mp} kg)")

else:
    st.info("👈 Ajusta los parámetros en el panel izquierdo y presiona 'CALCULAR BALANCE'")

# Footer
st.markdown("---")
st.markdown("*Dashboard de Balance de Masa - Deshidratación de Arándano*")
