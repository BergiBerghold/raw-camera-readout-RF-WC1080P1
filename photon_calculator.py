fraction_of_photons_on_sensor = 0.001481
shunt_resistor = 33000
inv_elementary_charge = 6.24150907 * 10**18


def calculate_flux(DAC_steps):
    pwm_voltage = 3.3 * DAC_steps / 65535
    current_through_led = pwm_voltage / shunt_resistor
    photon_flux_sensor = current_through_led * inv_elementary_charge * fraction_of_photons_on_sensor

    return int(photon_flux_sensor)


if __name__ == '__main__':
    print(calculate_flux(1) / 10 ** 6)