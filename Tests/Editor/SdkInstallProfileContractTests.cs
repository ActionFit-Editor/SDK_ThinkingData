#if UNITY_EDITOR
using NUnit.Framework;

namespace ActionFit.ThinkingData.Tests
{
    public sealed class SdkInstallProfileContractTests
    {
        [Test]
        public void Profile_IsValidAndOwnedByThisBridgePackage()
        {
            ActionFitSdkInstallProfile profile = ActionFitSdkInstallApi.ReadProfile(
                "Packages/com.actionfit.sdk.thinkingdata/Editor/SDKInstallProfile.json");

            Assert.That(profile.BridgePackageId, Is.EqualTo("com.actionfit.sdk.thinkingdata"));
            Assert.That(profile.ProfileVersion, Is.EqualTo("3.4.2"));
            Assert.That(
                profile.Sources[0].ImmutableRevision,
                Is.EqualTo("c2246848bd759a67a53d2eae61b7c466b9ac6f71"));
            Assert.That(ActionFitSdkInstallProfileValidator.Validate(profile).Success, Is.True);
        }
    }
}
#endif
