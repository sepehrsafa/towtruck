import pika
from app.models.user import UserAccount
from app.models.accident import Accident

# Set up RabbitMQ connection
params = pika.URLParameters(
    "amqps://mdlycema:wXVHNWrJvRez-7GSgzICeRHQpduI8s3-@toad.rmq.cloudamqp.com/mdlycema"
)
connection = pika.BlockingConnection(params)
channel = connection.channel()


async def check_if_assign_is_possible(station_id: int):

    # Get all users assigned to the station
    user = await UserAccount.filter(
        station_id=station_id, is_user_on_duty=False
    ).first()

    # check if query set is empty
    if not user:
        return False

    method_frame, header_frame, body = channel.basic_get(
        queue=f"station_{station_id}_queue", auto_ack=True
    )

    if method_frame:
        print("Received %r" % body)
        # turn body into a dictionary
        accident = await Accident.get(id=int(body))
        accident.assigned_to = user
        await accident.save()

        print(f"Assigned {user.username} to accident {accident.id}")

        user.is_user_on_duty = True
        await user.save()

        print(f"{user.username} is now on duty")

    else:
        print("No message returned")

    return True
