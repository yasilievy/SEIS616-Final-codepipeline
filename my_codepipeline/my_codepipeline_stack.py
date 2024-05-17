from aws_cdk import (
    # Duration,
    Stack,
    aws_codecommit as CodeCommit,
    aws_codebuild as CodeBuild,
    aws_codepipeline as CodePipeline,
    aws_codepipeline_actions as CodePipelineActions,
    aws_s3 as s3,
    aws_iam as iam
)
from constructs import Construct

class MyCodepipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # creating the CodeCommit repository. also does a directory input to find
        # the java-project.zip file
        repo = CodeCommit.Repository(self, "Repository",
            repository_name= "java-project",
            description="The repository",
            code=CodeCommit.Code.from_zip_file("java-project.zip", "main"))
        
        
        # creating a role with policy for the CodeBuild project
        app_build_role = iam.Role(self,"AppBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"))
        # app_build_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("CodeBuildAccess"))
        
        # creating a policy document for the BuildLogPolicy
        # policy_document = iam.PolicyDocument(statements=[iam.PolicyStatement(
        #     resources=["*"],
        #     actions=["logs:CreateLogGroup",
        #             "logs:CreateLogStream",
        #             "logs:PutLogEvents"]
        #     )])
        # build_log_policy = iam.Policy(self,"BuildLogPolicy",
        #     document=policy_document)
        
        
        # creating a policy statement to add to the artifact bucket
        # bucket_policy_statement = iam.PolicyStatement(
        #     resources=["*"],
        #     actions=["s3:PutObject"],
        #     effect=iam.Effect.DENY)
        # bucket_policy_statement.add_any_principal()
        
        # creating an S3 bucket for the CodeBuild project
        artifact_bucket = s3.Bucket(self,"ArtifactBucket")
        # artifact_bucket.add_to_resource_policy(bucket_policy_statement)
        
        # creating a CodeBuild project. inserts the s3 bucket, iam role, and
        # CodeCommit repository
        project = CodeBuild.PipelineProject(self,"AppBuildProject",
            environment=CodeBuild.BuildEnvironment(
                privileged=True
            ),
            role=app_build_role
        )
        
        # creating a role with policy for the CodePipeline
        codepipeline_service_role = iam.Role(self,"CodePipelineServiceRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"))
        
        
        
        code_pipeline = CodePipeline.Pipeline(self,"AppCodePipeline",
            artifact_bucket=artifact_bucket,
            role=codepipeline_service_role,
            stages=[CodePipeline.StageProps(
                stage_name="Source",
                actions=[
                    CodePipeLineActions.S3DeployAction(
                        action_name="GetSource"),
                    CodePipelineActions.CodeBuildAction(
                        action_name="BuildSource")]
                )])
        
        