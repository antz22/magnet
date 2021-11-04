import re
import numpy as np
import streamlit as st

from magnet import config
from magnet.constants import material_names, excitations
from magnet.plots import waveform_visualization, core_loss_multiple
from magnet.core import loss
from magnet.simplecs.simfunctions import SimulationPLECS


def ui_core_loss_predict():
    material = st.sidebar.selectbox('Material:', material_names)
    excitation = st.sidebar.selectbox('Excitation:', excitations + ("Arbitrary", "Simulated"))
    algorithm = st.sidebar.selectbox('Algorithm:', ('iGSE', 'Machine Learning'))

    if excitation in ('Datasheet', 'Sinusoidal'):

        col1, col2 = st.columns(2)
        with col1:
            st.header("Please provide waveform information")
            Freq = st.slider('Frequency (Hz)', 10000, 500000, 250000, step=1000)
            Flux = st.slider('Peak to Peak Flux Density (mT)', 10, 300, 150, step=1)
            Bias = st.slider('DC Bias (mT)', -300, 300, 0, step=10)
            duty_list = np.linspace(0, 1, 101)
            flux_read = np.multiply(np.sin(np.multiply(duty_list, np.pi * 2)), Flux / 2)
            flux_list = np.add(flux_read, Bias)

        with col2:
            waveform_visualization(st, x=duty_list, y=flux_list)

        st.header(f'{material}, {excitation}, f={Freq} Hz, \u0394B={Flux} mT, Bias={Bias} mT')

        core_loss = loss(waveform='sine', algorithm=algorithm, material=material, freq=Freq, flux_p2p=Flux)
        st.title(f'{algorithm} Core Loss: {core_loss} kW/m^3')

        col1, col2 = st.columns(2)
        with col1:
            core_loss_multiple(
                st,
                x=config.streamlit.core_loss_freq,
                y1=[loss(waveform='sine', algorithm='iGSE', material=material, freq=i, flux_p2p=Flux) for i in config.streamlit.core_loss_freq],
                y2=[loss(waveform='sine', algorithm='ML', material=material, freq=i, flux_p2p=Flux) for i in config.streamlit.core_loss_freq],
                title=f'Core Loss with Fixed Flux Density {Flux} mT',
                x_title='Frequency [Hz]'
            )

        with col2:
            core_loss_multiple(
                st,
                x=config.streamlit.core_loss_flux,
                y1=[loss(waveform='sine', algorithm='iGSE', material=material, freq=Freq, flux_p2p=i) for i in config.streamlit.core_loss_flux],
                y2=[loss(waveform='sine', algorithm='ML', material=material, freq=Freq, flux_p2p=i) for i in config.streamlit.core_loss_flux],
                title=f'Core Loss with Fixed Frequency {Freq} Hz',
                x_title='Flux Density [mT]'
            )

    if excitation == "Triangle":

        col1, col2 = st.columns(2)
        with col1:
            st.header("Please provide waveform information")
            Freq = st.slider('Frequency (Hz)', 10000, 500000, 250000, step=1000)
            Flux = st.slider('Peak to Peak Flux Density (mT)', 10, 300, 150, step=10)
            Duty = st.slider('Duty Ratio', 0.0, 1.0, 0.5, step=0.01)
            Bias = st.slider('DC Bias (mT)', -300, 300, 0, step=10)
            duty_list = [0, Duty, 1]
            flux_read = [0, Flux, 0]
            flux_mean = Flux / 2
            flux_diff = Bias - flux_mean
            flux_list = np.add(flux_read, flux_diff)

        with col2:
            waveform_visualization(st, x=duty_list, y=flux_list)

        st.header(f'{material}, {excitation}, f={Freq} Hz \u0394B={Flux} mT, D={Duty}, Bias={Bias} mT')

        core_loss = loss(waveform='sawtooth', algorithm=algorithm, material=material, freq=Freq, flux_p2p=Flux, duty_ratio=Duty)
        st.title(f'{algorithm} Core Loss: {core_loss} kW/m^3')

        col1, col2, col3 = st.columns(3)
        with col1:
            core_loss_multiple(
                st,
                x=config.streamlit.core_loss_freq,
                y1=[loss(waveform='sawtooth', algorithm='iGSE', material=material, freq=i, flux_p2p=Flux, duty_ratio=Duty) for i in config.streamlit.core_loss_freq],
                y2=[loss(waveform='sawtooth', algorithm='ML', material=material, freq=i, flux_p2p=Flux, duty_ratio=Duty) for i in config.streamlit.core_loss_freq],
                title=f'Core Loss with F Sweep at {Flux} mT and D={Duty}',
                x_title='Frequency [Hz]'
            )

        with col2:
            core_loss_multiple(
                st,
                x=config.streamlit.core_loss_flux,
                y1=[loss(waveform='sawtooth', algorithm='iGSE', material=material, freq=Freq, flux_p2p=i, duty_ratio=Duty) for i in config.streamlit.core_loss_flux],
                y2=[loss(waveform='sawtooth', algorithm='ML', material=material, freq=Freq, flux_p2p=i, duty_ratio=Duty) for i in config.streamlit.core_loss_flux],
                title=f'Core Loss with B Sweep at {Freq} Hz and D={Duty}',
                x_title='Flux Density [mT]'
            )

        with col3:
            core_loss_multiple(
                st,
                x=config.streamlit.core_loss_duty,
                y1=[loss(waveform='sawtooth', algorithm='iGSE', material=material, freq=Freq, flux_p2p=Flux, duty_ratio=i) for i in config.streamlit.core_loss_duty],
                y2=[loss(waveform='sawtooth', algorithm='ML', material=material, freq=Freq, flux_p2p=Flux, duty_ratio=i) for i in config.streamlit.core_loss_duty],
                title=f'Core Loss with D Sweep at {Freq} Hz and {Flux} mT',
                x_title='Duty Ratio'
            )

    if excitation == "Trapezoidal":

        col1, col2 = st.columns(2)
        with col1:
            st.header("Please provide waveform information")
            Freq = st.slider('Frequency (Hz)', 10000, 500000, step=1000)
            Flux = st.slider('Peak to Peak Flux Density (mT)', 10, 300, step=10)
            Duty1 = st.slider('Duty Ratio 1', 0.0, 1.0, 0.25, step=0.01)
            Duty2 = st.slider('Duty Ratio 2', 0.0, 1.0, 0.5, step=0.01)
            Duty3 = st.slider('Duty Ratio 3', 0.0, 1.0, 0.75, step=0.01)
            Bias = st.slider('DC Bias (mT)', -300, 300, 0, step=10)
            duty_list = [0, Duty1, Duty2, Duty3, 1]
            flux_read = [0, Flux, Flux, 0, 0]
            flux_mean = Flux / 2
            flux_diff = Bias - flux_mean
            flux_list = np.add(flux_read, flux_diff)

        with col2:
            waveform_visualization(st, x=duty_list, y=flux_list)

        st.header(f'{material}, {excitation}, f={Freq} Hz, \u0394B={Flux} mT, D1={Duty1}, D2={Duty2}, D3={Duty3}, Bias={Bias} mT')

        duty_ratios = [Duty1, Duty2, Duty3]
        core_loss = loss(waveform='trapezoid', algorithm=algorithm, material=material, freq=Freq, flux_p2p=Flux, duty_ratios=duty_ratios)
        st.title(f'{algorithm} Core Loss: {core_loss} kW/m^3')

        col1, col2 = st.columns(2)
        with col1:
            core_loss_multiple(
                st,
                x=config.streamlit.core_loss_freq,
                y1=[loss(waveform='trapezoid', algorithm='iGSE', material=material, freq=i, flux_p2p=Flux, duty_ratios=duty_ratios) for i in config.streamlit.core_loss_freq],
                y2=[loss(waveform='trapezoid', algorithm='ML', material=material, freq=i, flux_p2p=Flux, duty_ratios=duty_ratios) for i in config.streamlit.core_loss_freq],
                title=f'Core Loss with Fixed Flux Density {Flux} mT',
                x_title='Frequency [Hz]'
            )

        with col2:
            core_loss_multiple(
                st,
                x=config.streamlit.core_loss_flux,
                y1=[loss(waveform='trapezoid', algorithm='iGSE', material=material, freq=Freq, flux_p2p=i, duty_ratios=duty_ratios) for i in config.streamlit.core_loss_flux],
                y2=[loss(waveform='trapezoid', algorithm='ML', material=material, freq=Freq, flux_p2p=i, duty_ratios=duty_ratios) for i in config.streamlit.core_loss_flux],
                title=f'Core Loss with Fixed Frequency {Freq} Hz',
                x_title='Flux Density [mT]'
            )

    if excitation == "Arbitrary":

        col1, col2 = st.columns(2)
        with col1:
            Freq = st.slider('Cycle Frequency (Hz)', 10000, 500000, step=1000)
            duty_string = st.text_input('Waveform Pattern Duty in a Cycle (%)',
                                        [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
            flux_string = st.text_input('Waveform Pattern Relative Flux Density (mT)',
                                        [0, 10, 20, 10, 20, 30, -10, -30, 10, -10, 0])
            Bias = st.slider('DC Bias (mT)', -300, 300, 0, step=10)

            duty_list = [float(i) for i in re.findall(r"[-+]?\d*\.?\d+|[-+]?\d+", duty_string)]
            flux_read = [float(i) for i in re.findall(r"[-+]?\d*\.?\d+|[-+]?\d+", flux_string)]
            flux_mean = np.average(flux_read)
            flux_diff = Bias - flux_mean
            flux_list = np.add(flux_read, flux_diff)

        with col2:
            waveform_visualization(st, x=duty_list, y=flux_list)

        core_loss = loss(waveform='arbitrary', algorithm=algorithm, material=material, freq=Freq, flux=flux_list, frac_time=duty_list)
        st.title(f'{algorithm} Core Loss: {core_loss} kW/m^3')

    if excitation == 'Simulated':
        core_loss = SimulationPLECS(material, algorithm)
        st.title(f'{algorithm} Core Loss: {core_loss} kW/m^3')