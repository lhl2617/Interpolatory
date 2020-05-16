import * as React from 'react';

const logo = require('../../../../../assets/img/logo.png').default;

const Info = () => {

    return (
        <div style={{ textAlign: 'center', margin: 'auto' }}>
            <div>
                <img src={logo} alt='Interpolatory Simulator' style={{ marginTop: 12, maxWidth: 200, marginBottom: 12 }} />
                <h2 style={{ fontSize: 36, fontWeight: 800, marginBottom: 0 }}>Interpolatory Simulator v0.0.1</h2>
                <h4>Video frame-rate interpolation framework for software simulation and benchmarking</h4>
            </div>

            <div style={{ marginTop: 200 }}>
                <h3>©2020 Interpolatory - Interpolatory Simulator</h3>
                <p style={{ marginBottom: 0, fontSize: 14 }}>Naim Govani | Olly Larkin | Lin Hao Lee | Jialong Yu | Navid Zandpour | Zhiyuan Zhang</p>
                <p style={{ marginBottom: 0, fontSize: 14 }}>With thanks to Kieron Turkington (Intel Corporation United Kingdom) and</p>
                <p style={{ marginBottom: 0, fontSize: 14 }}>Professor G.A. Constantinides (Imperial College London)</p>
            </div>
        </div>

    )

}

export default Info;