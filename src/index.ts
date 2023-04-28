import { FlashbotsBundleProvider } from '@flashbots/ethers-provider-bundle';
import { BigNumber, Wallet, providers } from 'ethers';
import * as dotenv from 'dotenv';
dotenv.config();

// select chain id
const CHAIN_ID = 1;

// mainnet
// const provider = new providers.JsonRpcProvider(process.env.ALCHEMY_MAINNET);
// const FLASHBOTS_ENDPOINT = 'https://relay.flashbots.net';
// const FALLBACK_CONTRACT = '0xE07C1FA616f64205d216f8db4883e17801b80B85';

// goerli
const FALLBACK_CONTRACT = '0x06d5ECe5E37439729C3D236A711e5e4729D8c3e2';
const FAKE_MINTER = '0x1c7eB6b9c647832998CeFdc445d9B059DbeED8C9';
const FLASHBOTS_ENDPOINT = 'https://relay-goerli.flashbots.net';
const provider = new providers.JsonRpcProvider(process.env.ALCHEMY_PROVIDER);

if (process.env.ETH_SIGNER_KEY === undefined) {
	console.error('Please provide ETH_SIGNER_KEY');
	process.exit(1);
}
const wallet = new Wallet(process.env.ETH_SIGNER_KEY, provider);
const GWEI = BigNumber.from(10).pow(9);
const ETHER = BigNumber.from(10).pow(18);

async function main() {
	const flashbots_provider = await FlashbotsBundleProvider.create(
		provider,
		Wallet.createRandom(),
		FLASHBOTS_ENDPOINT
	);
	provider.on('block', async (blocknumber) => {
		console.log(blocknumber);
		const bundle_submit_response = await flashbots_provider.sendBundle(
			[
				// mainnet

				// {
				// 	transaction: {
				// 		chainId: CHAIN_ID,
				// 		type: 2,
				// 		value: BigNumber.from(0),
				// 		data: '0x',
				// 		gasPrice: 50000,
				// 		maxFeePerGas: GWEI.mul(3),
				// 		maxPriorityFeePerGas: GWEI.mul(2),
				// 		to: FALLBACK_CONTRACT,
				// 	},
				// 	signer: wallet,
				// },

				// goerli

				{
					transaction: {
						chainId: CHAIN_ID,
						type: 2,
						value: BigNumber.from(0),
						data: '0x',
						maxFeePerGas: GWEI.mul(3),
						maxPriorityFeePerGas: GWEI.mul(2),
						to: FALLBACK_CONTRACT,
					},
					signer: wallet,
				},
				{
					transaction: {
						chainId: CHAIN_ID,
						type: 2,
						value: ETHER.div(1000).mul(1),
						data: '0x1249c58b',
						maxFeePerGas: GWEI.mul(3),
						maxPriorityFeePerGas: GWEI.mul(2),
						to: FAKE_MINTER,
					},
					signer: wallet,
				},
			],
			blocknumber + 1
		);
		if ('error' in bundle_submit_response) {
			console.log(bundle_submit_response.error.message);
			return;
		}
		console.log(await bundle_submit_response.simulate());
	});
}

main();
