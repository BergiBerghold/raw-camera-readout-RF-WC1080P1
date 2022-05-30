fraction_of_photons_on_sensor = 0.00723
shunt_resistor = 33000


def calculate_flux(DAC_steps):
    pwm_voltage = 3.3 * DAC_steps / 65535
    current_through_led = pwm_voltage / shunt_resistor
    photon_flux_sensor = current_through_led * fraction_of_photons_on_sensor

    return photon_flux_sensor

