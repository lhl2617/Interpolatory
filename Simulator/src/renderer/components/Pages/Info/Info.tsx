import * as React from 'react';
import * as cp from 'child_process';

type PyVer = { status: "loading" | "done" | "error", ver: string };

type IState = {
    pyVer: PyVer;
}

export class Info extends React.Component<{}, IState> {
    constructor(props: any) {
        super(props);
        this.state = {
            pyVer: { status: "loading", ver: "" },
        };
    }

    componentDidMount = () => {
        this.getPyVer()
    }

    getPyVer = async () => {
        const proc = cp.spawn(`python3`, [`-V`]);

        proc.stdout.on('data', (data) => {
            this.setState({ pyVer: { status: "done", ver: data.toString() } });
        });


        proc.on('close', (code) => {
            if (code !== 0) {
                this.setState({ pyVer: { status: "error", ver: this.state.pyVer.ver } });
            }
        })
    }

    renderPyVer = (pyVer: PyVer) => {
        if (pyVer.status === "loading") {
            return "Loading...";
        }
        if (pyVer.status === "error") {
            return "Error! Could not get Python version."
        }
        return pyVer.ver;
    }

    render() {
        const { pyVer } = this.state;
        return (
            <div>
                <div style={{ marginBottom: 48 }}>
                    <h3>Machine Info</h3>
                    <p style={{ marginBottom: 0 }}>Python Version: {this.renderPyVer(pyVer)}</p>

                </div>
                <div style={{ textAlign: 'center', margin: 'auto' }}>
                    <h3>©2020 Interpolatory - Interpolatory Simulator</h3>
                    <p style={{ marginBottom: 0 }}>Naim Govani | Olly Larkin | Lin Hao Lee | Jialong Yu | Navid Zandpour | Zhiyuan Zhang</p>
                    <p style={{ marginBottom: 0 }}>With thanks to Kieron Turkington (Intel Corporation United Kingdom) and</p>
                    <p style={{ marginBottom: 0 }}>Professor G.A. Constantinides (Imperial College London)</p>
                </div>
            </div>

        )
    }

}

export default Info;