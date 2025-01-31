---
title: 'Switching from NVM to Volta'
author: Janusz Lavrnja-Czapski
categories:
  - Development
tags:
  - javascript
  - node
  - tooling
  - performance
---

### The problem
Developers using WSL as their established environment have no issue switching between Node versions using `nvm`, whereas this operation requires admin rights for Windows users running outside of WSL.

Obtaining admin rights can be a bit of a slow process and is much too slow for something as simple as switching Node versions. Could Volta provide a cross-platform solution that is more straightforward to manage compared to `nvm`?

### Why switch?

- Faster than NVM.
- Runs using a shim instead of symlinks so doesn't require admin rights for Windows users.
- Can manage Node dependencies in `package.json` instead of having to have a dedicated `.nvmrc` file.
- Automatically switches Node versions when `cd`'ing between projects, functionality that required a custom script with `nvm`.

### How to switch

Run these commands in your root directory:

`rm -rf ~/.nvm`
`rm -rf ~/.npm`
`rm -rf ~/.bower`

Remove `source ~/.nvm` from your `.bashrc` or `.zshrc`, along with any other references to `nvm`.

**Volta installation**

For Mac/Unix systems, run `curl https://get.volta.sh | bash` or for Windows run `winget install Volta.Volta`. More detailed information can be found in the [documentation](https://docs.volta.sh/guide/getting-started).

To globally install a LTS Node version, run `volta install node` in your root directory, or to install a specific version, run like so `volta install node@22.5.1`.

**Pinning dependencies**

If you want to manage a specific Node version within a project, `cd` into your project folder and run `volta pin node@20.16` at the root level of the project, replacing the version number with your own.

```
"volta": {
  "node": "20.16.0"
}
```

You'll see that this will create the above entry in your `package.json` which can then be commited to source control. When any other developers with Volta installed pull down this repository and access it via the command line, it will automatically switch their Node version to the one specified.

**Testing the auto-switch**

Now `cd` into another project and run `volta pin node@<new-version-number>`.

Run `node -v` and see the new version number listed. Now `cd` back into your other project with a pinned Node version in the `package.json` and run `node -v` again.

You should see the version number updated automatically without any custom script or configuration!

### Moving forward

Volta seems like a great tool to manage Node versions in a more consistent way across teams with different development environments, less manual intervention and nice fancy features included out-of-the-box.
