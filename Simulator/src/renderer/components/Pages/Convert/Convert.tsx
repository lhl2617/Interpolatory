import * as React from 'react';
import { Input, Form, message } from 'antd';
import { remote } from 'electron';
import * as cp from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { binName } from '../../../consts';

const { Search } = Input;
/*
{'plugin': 'ffmpeg', 'nframes': 8736, 'ffmpeg_version': '4.1 built with gcc 8.2.1 (GCC) 20181017', 'codec': 'h264', 'pix_fmt': 'yuv420p(progressive)', 'fps': 60.0, 'source_size': (1920, 1080), 'size': (1920, 1080), 'duration': 145.6}
*/
type VideoMetadata = {
    nframes: number,
    codec: string,
    fps: number,
    source_size: number[],
    duration: number
};

const pleaseInput = `Please input source video path.`;

type IState = {
    inputVideoPath: string;
    inputVideoMetadata: VideoMetadata | undefined;
    inputValidator: { status: "success" | "error"; help: string }
    outputVideoPath: string;
    outputValidator: { status: "success" | "error"; help: string }
    targetFPS: number;
    startTime: number;
    endTime: number;
}

export class Convert extends React.Component<{}, IState> {
    constructor(props: any) {
        super(props);
        this.state = {
            inputVideoPath: ``,
            inputVideoMetadata: undefined,
            inputValidator: { status: `error`, help: pleaseInput },
            outputVideoPath: ``,
            outputValidator: { status: `error`, help: pleaseInput },
            targetFPS: 60,
            startTime: 0,
            endTime: 60,
        };
    }

    setOutputFilePath = async (filePath: string) => {
        this.setState({
            outputVideoPath: filePath,
        });

        const { inputVideoPath } = this.state;
        const srcExt = path.extname(inputVideoPath);



        // match extensions
        if (srcExt !== path.extname(filePath)) {
            this.setState({
                outputValidator: { status: "error", help: "File extensions do not match" }
            })
        }

    }

    setInputFilePath = async (filePath: string) => {
        // console.log(`Setting filePath to ${filePath}`);

        this.setState({
            inputVideoPath: filePath,
        })

        // check exists first
        const fileExists = fs.existsSync(filePath);
        if (fileExists) {
            // load into python
            const args = [binName, `-m`, filePath];
            const proc = cp.spawn(`python3`, args)

            let stdoutData: VideoMetadata;
            proc.stdout.on('data', (data) => {
                // console.log(`Gotten stdout: ${data}`);
                stdoutData = JSON.parse(data);
                this.setState({
                    inputVideoMetadata: stdoutData,
                })
            })

            proc.stderr.on('data', (data) => {
                // message.error(data.toString())
            })

            proc.on('close', (code) => {
                if (code === 0) {
                    // in here we need to set also the outputVideoPath
                    const fileName = path.basename(filePath);
                    const fileExt = path.extname(fileName);
                    const fileDir = path.dirname(filePath);

                    const outputPath = `${fileDir}${path.sep}${fileName}_output.${fileExt}`

                    this.setOutputFilePath(outputPath);

                    this.setState({
                        inputValidator: { status: "success", help: "" }
                    })
                }
                else {
                    this.setState({
                        inputValidator: { status: "error", help: filePath.length === 0 ? pleaseInput : 'Format is not supported.' }
                    })
                }
            })
        }
        else {
            this.setState({
                inputValidator: { status: "error", help: filePath.length === 0 ? pleaseInput : 'File does not exist.' }
            })
        }
    }

    parseMetadata = (metadata: VideoMetadata | undefined) => {
        if (!metadata) {
            return <div>N/A</div>
        }
        const { nframes, codec, fps, source_size, duration } = metadata;
        return (
            <div>
                <div>{`Codec: ${codec}`}</div>
                <div>{`Number of frames: ${nframes}`}</div>
                <div>{`FPS: ${fps}`}</div>
                <div>{`Dimensions: ${source_size[0]}x${source_size[1]}`}</div>
                <div>{`Duration: ${duration}s`}</div>
            </div>
        );
    }

    render() {
        const { inputVideoPath, inputVideoMetadata, outputVideoPath, targetFPS, startTime, endTime, inputValidator, outputValidator } = this.state;

        const disabled = inputValidator.status === "error";

        return (
            <div>
                <Form layout="vertical" >
                    <Form.Item
                        label={<h3>Source Video Path</h3>}
                        validateStatus={inputValidator.status}
                        help={inputValidator.help}
                    >
                        <Search
                            enterButton="Browse"
                            value={inputVideoPath}
                            onChange={(e) => this.setInputFilePath(e.target.value)}
                            onSearch={() => {
                                const filePath = remote.dialog.showOpenDialogSync(
                                    { properties: ['openFile'], filters: [{ name: 'Videos', extensions: ['mov', 'avi', 'mpg', 'mpeg', 'mp4', 'mkv', 'wmv'] }] }
                                );

                                if (filePath && filePath.length) {
                                    this.setInputFilePath(filePath[0]);
                                }
                            }}
                        />
                    </Form.Item>

                    <h3>Source Video Metadata</h3>
                    {this.parseMetadata(inputVideoMetadata)}
                </Form>


                <Form.Item
                    label={<h3>Destination Video Path</h3>}
                    validateStatus={outputValidator.status}
                    help={outputValidator.help}
                >
                    <Search
                        enterButton="Browse"
                        value={outputVideoPath}
                        onChange={(e) => this.setOutputFilePath(e.target.value)}
                        onSearch={() => {
                            const srcExtension = path.extname(inputVideoPath)

                            const filePath = remote.dialog.showOpenDialogSync(
                                { properties: ['openFile'], filters: [{ name: 'Videos', extensions: ['mov', 'avi', 'mpg', 'mpeg', 'mp4', 'mkv', 'wmv'] }] }
                            )

                            if (filePath && filePath.length) {
                                this.setOutputFilePath(filePath[0]);
                            }
                        }}
                    />
                </Form.Item>

            </div>
        )
    }

}

export default Convert;