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

        # creating a policy document for the BuildLogPolicy and inserts into
        # the BuildLogPolicy
        policy_document = iam.PolicyDocument(statements=[iam.PolicyStatement(
            resources=["*"],
            actions=["logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"])])
        build_log_policy = iam.Policy(self,"BuildLogPolicy",
            document=policy_document)
        

        # creating an S3 bucket for the CodePipeline pipeline. inserts policy
        # statement
        artifact_bucket = s3.Bucket(self,"ArtifactBucket")
        bucket_policy_statement = iam.PolicyStatement(
            resources=["*"],
            actions=["s3:PutObject"],
            effect=iam.Effect.DENY)
        bucket_policy_statement.add_any_principal()
        artifact_bucket.add_to_resource_policy(bucket_policy_statement)
        

        # creating a CodeBuild project. inserts the s3 bucket, iam role, and
        # CodeCommit repository
        project = CodeBuild.PipelineProject(self,"AppBuildProject",
            environment=CodeBuild.BuildEnvironment(
                privileged=True
            ),
            role=app_build_role
        )
        
        deploy_input = CodePipeline.Artifact()
        
        # creating a role with policy for the CodePipeline
        codepipeline_service_role = iam.Role(self,"CodePipelineServiceRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"))
        
        # creating a CodePipeline pipeline. inserts the s3 bucket and iam role
        code_pipeline = CodePipeline.Pipeline(self,"AppCodePipeline",
            artifact_bucket=artifact_bucket,
            role=codepipeline_service_role,
            )
        # creating a stage with CodeCommit action. inserts the input artifact,
        # repo and declares this stage to run first
        source_stage = code_pipeline.add_stage(stage_name="Source")
        source_stage.add_action(CodePipelineActions.CodeCommitSourceAction(
            action_name="GetSource",
            output=deploy_input,
            repository=repo,
            run_order=1))
        
        # creating a stage with CodeBuild action. inserts the input artifact,
        # CodeBuild project, and declares this stage to run second
        build_stage = code_pipeline.add_stage(stage_name="Build")
        build_stage.add_action(CodePipelineActions.CodeBuildAction(
            action_name="BuildSource",
            input=deploy_input,
            run_order=2,
            project=project))
        
        