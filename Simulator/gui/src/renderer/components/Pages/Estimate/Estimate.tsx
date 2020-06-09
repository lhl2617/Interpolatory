import * as React from 'react';
import { Input, Form, Select, message, Button, Modal, Progress, Popconfirm, Spin, InputNumber } from 'antd';
import { remote } from 'electron';
import * as cp from 'child_process';
import * as path from 'path';
import { getPython3, getInterpolatory, InterpolationMode, iModeToString, iModeToPrettyString } from '../../../util';
import IMode from '../../IMode/IMode';

message.config({ top: 64, maxCount: 3 })


const python3 = getPython3();
const binName = getInterpolatory();

// estimation process
let estProc: cp.ChildProcessWithoutNullStreams | undefined;

type IState = {
    iMode: InterpolationMode | undefined;
    frameWidth: number;
    frameHeight: number;
    estimateState: "done" | "error" | "estimating" | "idle";
    overrideDisable: boolean;
    results?: Record<string, string>;
}

class Estimate extends React.Component<{}, IState> {
    mounted = false;
    constructor(props: any) {
        super(props)
        this.state = {
            iMode: undefined,
            frameWidth: 1920,
            frameHeight: 1080,
            estimateState: `idle`,
            overrideDisable: false,
            results: undefined
        }
    }

    _setState = (obj: Partial<IState>) => {
        if (this.mounted)
            this.setState(obj as any);
    }

    componentDidMount = () => {
        this.mounted = true;
    };

    componentWillUnmount = () => {
        this.mounted = false;
        this.resetEstimate();
    }

    resetEstimate = async () => {
        this._setState({ overrideDisable: true, estimateState: `idle` });
        const updateState = () => {
            this._setState({
                estimateState: `idle`,
                overrideDisable: false
            })
        }
        if (estProc) {
            estProc.kill(`SIGKILL`);
            estProc = undefined;
        }
        setTimeout(() => updateState(), 3000);
    }

    setIMode = async (iMode: InterpolationMode) => {
        this._setState({ iMode: iMode })
    }

    startEstimate = async () => {
        this._setState({ estimateState: `estimating` });
        const { iMode, frameWidth, frameHeight } = this.state;

        if (!iMode) {
            message.error(`Interpolation Mode not set!`)
            return;
        }

        const interpolationMode = iModeToString(iMode)

        const args = [binName, `-e`, interpolationMode, frameWidth.toString(), frameHeight.toString(), `-gui`];
        console.log(`go!`)

        estProc = cp.spawn(python3, args, { cwd: path.dirname(binName) })

        let gotStderr = ``

        estProc.stdout.on(`data`, (data) => {
            const res: Record<string, string> = JSON.parse(data);
            this._setState({ results: res, estimateState: `done` })
        });

        estProc.stderr.on(`data`, (data) => {
            gotStderr += data.toString();
            console.error(data.toString())
        })

        estProc.on(`close`, (code) => {
            if (code !== 0 && estProc) {
                message.error(`Estimation failed: ${gotStderr.length ? gotStderr : `Unknown error`}`)
                if (this.state.estimateState !== `idle`) this._setState({ estimateState: `error` });
            }
            estProc = undefined;
        })

    }

    render = () => {
        const { frameHeight, frameWidth, estimateState, overrideDisable, iMode, results } = this.state

        return (
            <div>
                <h2>Estimate hardware DDR usage</h2>
                <Form layout="vertical" >
                    <Form.Item
                        label="Frame Width"
                    >
                        <InputNumber min={1} step={1}
                            onChange={(optionValue) => optionValue && this._setState({ frameWidth: typeof optionValue === 'number' ? optionValue : parseInt(optionValue) })} value={frameWidth} />
                    </Form.Item>
                </Form>
                <Form layout="vertical" >
                    <Form.Item
                        label="Frame Height"
                    >
                        <InputNumber min={1} step={1}
                            onChange={(optionValue) => optionValue && this._setState({ frameHeight: typeof optionValue === 'number' ? optionValue : parseInt(optionValue) })} value={frameHeight} />
                    </Form.Item>
                    <IMode setIMode={this.setIMode} iMode={iMode} disabled={false} modeFlag="-e" />

                </Form>
                <div style={{ margin: 'auto', textAlign: 'center', marginTop: 48, marginBottom: 48 }}>
                    <Button onClick={this.startEstimate} size="large" disabled={overrideDisable || !iMode} type="primary">Start Estimation</Button>

                </div>

                <Modal
                    style={{ left: 100 }}
                    title='Estimate'
                    visible={estimateState !== `idle`}
                    footer={null}
                    closable={false}
                    maskClosable={false}
                >

                    <h4>Frame Width</h4>
                    <p>{frameWidth}</p>
                    <h4>Frame Height</h4>
                    <p>{frameHeight}</p>
                    <h4>Interpolation Mode</h4>
                    <p>{iMode && iModeToPrettyString(iMode)}</p>
                    <h4>Output Frames Directory</h4>
                    {
                        (estimateState === `estimating`) && <div>
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>Estimating...</h4>
                            <div style={{ margin: `auto`, textAlign: `center`, marginTop: 12 }}>
                                <Spin size='large' />
                            </div>
                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                <Popconfirm
                                    title="This will stop estimating. Are you sure?"
                                    onConfirm={this.resetEstimate}
                                    okText='Yes'
                                    cancelText='No'
                                >
                                    <Button danger>Stop</Button>
                                </Popconfirm>
                            </div>
                        </div>
                    }
                    {
                        estimateState === `done` && <div>

                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `green` }}>Finished</h4>

                            {
                                results &&
                                <div style={{ textAlign: `center`, margin: `auto`, marginTop: 12 }}>
                                    <h4 style={{ fontWeight: 800 }}>Results</h4>

                                    {
                                        Object.entries(results).map(([key, val], i) =>
                                            <p key={i} style={{ margin: `auto` }}>{key}: {val}</p>
                                        )
                                    }
                                </div>


                            }

                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                <Button onClick={this.resetEstimate}>OK</Button>
                            </div>
                        </div>
                    }
                    {
                        estimateState === `error` && <div>
                            <h4 style={{ textAlign: `center`, margin: `auto`, marginTop: 12, color: `red` }}>An error occured.</h4>

                            <div style={{ textAlign: `center`, margin: `auto`, marginTop: 24 }}>
                                <Button onClick={this.resetEstimate}>OK</Button>
                            </div>
                        </div>
                    }
                </Modal>
            </div>
        )

    }

}

export default Estimate