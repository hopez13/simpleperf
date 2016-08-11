#!/usr/bin/env python
#
# Copyright (C) 2016 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Downloads simpleperf prebuilts from the build server."""
import argparse
import glob
import logging
import os
import shutil
import textwrap


THIS_DIR = os.path.realpath(os.path.dirname(__file__))


def logger():
    """Returns the main logger for this module."""
    return logging.getLogger(__name__)


def check_call(cmd):
    """Proxy for subprocess.check_call with logging."""
    import subprocess
    logger().debug('check_call `%s`', ' '.join(cmd))
    subprocess.check_call(cmd)


def fetch_artifact(branch, build, target, pattern):
    """Fetches and artifact from the build server."""
    logger().info('Fetching %s from %s %s (artifacts matching %s)', build,
                  target, branch, pattern)
    fetch_artifact_path = '/google/data/ro/projects/android/fetch_artifact'
    cmd = [fetch_artifact_path, '--branch', branch, '--target', target,
           '--bid', build, pattern]
    check_call(cmd)


def start_branch(build):
    """Creates a new branch in the project."""
    branch_name = 'update-' + (build or 'latest')
    logger().info('Creating branch %s', branch_name)
    check_call(['repo', 'start', branch_name, '.'])


def commit(branch, build, add_paths):
    """Commits the new prebuilts."""
    logger().info('Making commit')
    check_call(['git', 'add'] + add_paths)
    message = textwrap.dedent("""\
        Update NDK prebuilts to build {build}.

        Taken from branch {branch}.""").format(branch=branch, build=build)
    check_call(['git', 'commit', '-m', message])


def remove_old_release(install_dir):
    """Removes the old prebuilts."""
    if os.path.exists(install_dir):
        logger().info('Removing old install directory "%s"', install_dir)
        check_call(['git', 'rm', '-rf', '--ignore-unmatch', install_dir])

    # Need to check again because git won't remove directories if they have
    # non-git files in them.
    if os.path.exists(install_dir):
        shutil.rmtree(install_dir)


def install_new_release(branch, build):
    """Installs the new release."""
    for host in ('darwin', 'linux', 'windows'):
        install_host_components(branch, build, host)

    for arch in ('arm', 'arm64', 'mips', 'x86', 'x86_64'):
        install_device_components(branch, build, arch)

    install_repo_prop(branch, build)


def install_host_components(branch, build, host):
    """Installs the host specific components of the release."""
    os.makedirs(host)

    target = {
        'darwin': 'sdk_mac',
        'linux': 'sdk_x86_64-sdk',
        'windows': 'sdk',
    }[host]

    name = {
        'darwin': 'simpleperf_host',
        'linux': 'simpleperf_host',
        'windows': 'simpleperf.exe',
    }[host]

    fetch_artifact(branch, build, target, name)
    shutil.move(name, os.path.join(host, 'simpleperf'))


def install_device_components(branch, build, arch):
    """Installs the device specific components of the release."""
    install_dir = os.path.join('android', arch)
    os.makedirs(install_dir)

    target = {
        'arm': 'sdk_arm64-sdk',
        'arm64': 'sdk_arm64-sdk',
        'mips': 'sdk_mips-sdk',
        'x86': 'sdk_x86_64-sdk',
        'x86_64': 'sdk_x86_64-sdk',
    }[arch]

    name = {
        'arm': 'simpleperf32',
        'arm64': 'simpleperf',
        'mips': 'simpleperf',
        'x86': 'simpleperf32',
        'x86_64': 'simpleperf',
    }[arch]

    fetch_artifact(branch, build, target, name)
    shutil.move(name, os.path.join(install_dir, 'simpleperf'))


def install_repo_prop(branch, build):
    """Installs the repo.prop from the build for auditing."""
    # We took everything from the same build number, so we only need the
    # repo.prop from one of our targets.
    fetch_artifact(branch, build, 'sdk', 'repo.prop')


def get_args():
    """Parses and returns command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-b', '--branch', default='aosp-master',
        help='Branch to pull build from.')
    parser.add_argument('--build', required=True, help='Build number to pull.')
    parser.add_argument(
        '--use-current-branch', action='store_true',
        help='Perform the update in the current branch. Do not repo start.')
    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help='Increase output verbosity.')

    return parser.parse_args()


def main():
    """Program entry point."""
    os.chdir(THIS_DIR)

    args = get_args()
    verbose_map = (logging.WARNING, logging.INFO, logging.DEBUG)
    verbosity = args.verbose
    if verbosity > 2:
        verbosity = 2
    logging.basicConfig(level=verbose_map[verbosity])

    if not args.use_current_branch:
        start_branch(args.build)
    install_dirs = ['android', 'darwin', 'linux', 'windows']
    for install_dir in install_dirs:
        remove_old_release(install_dir)
    install_new_release(args.branch, args.build)
    commit(args.branch, args.build, install_dirs + ['repo.prop'])


if __name__ == '__main__':
    main()
