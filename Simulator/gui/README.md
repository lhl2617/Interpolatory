# Interpolatory Software Simulator GUI

## Usage
A pre-built 64-bit Windows Installer and binary is available upon request.

## Development

### Requirements
* Node (v12 and above)
* Python 3 (tested on 3.8.2 Windows & 3.6.2 Ubuntu 18.04)

### Getting started
Install dependencies
```bash
npm install
```
### Start Development
```bash
npm run start-dev
```

### Packaging
```bash
npm run dist
```

This will create a installer for your platform in the `releases` folder.

You can make builds for specific platforms (or multiple platforms) by using the options found [here](https://www.electron.build/cli). E.g. building for all platforms (Windows, Mac, Linux):

```bash
npm run dist -- -mwl
```